"""
Predictor engine for Phishing Email Classifier.
Extracts features, runs ML models, and produces detailed security diagnostics.
"""

import os
import re
import email
from email.message import EmailMessage
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import numpy as np
import joblib
from scipy.sparse import hstack

from run_simple import (
    FEATURE_FUNCS,
    clean_text,
    get_email_text,
    get_urls,
)

BUNDLE_PATH = os.path.join(os.path.dirname(__file__), "model_bundle.joblib")

class EmailPredictor:
    def __init__(self):
        self.bundle = None
        self.tfidf = None
        self.scaler = None
        self.models = {}
        self.benchmarks = []
        self.roc_data = {}
        self.dataset_stats = {}
        self.feature_importances = []
        self.feature_names = []
        self.load()

    def load(self):
        if not os.path.exists(BUNDLE_PATH):
            print(f"[*] Model bundle not found at {BUNDLE_PATH}. Automatically generating initial model bundle...")
            from train_and_cache import train_and_save
            train_and_save(half_limit=400)
        self.bundle = joblib.load(BUNDLE_PATH)
        self.tfidf = self.bundle["tfidf"]
        self.scaler = self.bundle["scaler"]
        self.models = self.bundle["models"]
        self.benchmarks = self.bundle["benchmarks"]
        self.roc_data = self.bundle["roc_data"]
        self.dataset_stats = self.bundle["dataset_stats"]
        self.feature_importances = self.bundle["feature_importances"]
        self.feature_names = self.bundle["feature_names"]

    def parse_input_to_email(self, raw_input: str, sender: str = None, recipient: str = None, subject: str = None):
        """Converts raw input or structured fields into an email.message object."""
        # If user provided separate fields
        if sender or recipient or subject:
            msg = EmailMessage()
            msg['From'] = sender or "user@example.com"
            msg['To'] = recipient or "recipient@example.com"
            msg['Subject'] = subject or "No Subject"
            if "<html" in raw_input.lower() or "<body" in raw_input.lower() or "<p" in raw_input.lower() or "<a " in raw_input.lower():
                msg.set_content(raw_input, subtype='html')
            else:
                msg.set_content(raw_input)
            return msg

        # Otherwise attempt to parse as RFC822 raw message
        try:
            msg = email.message_from_string(raw_input)
            # Check if headers actually existed or if it was just plain body text
            if not msg['From'] and not msg['To'] and not msg['Subject']:
                # It's likely just plain body text
                msg = EmailMessage()
                msg['From'] = "sender@example.com"
                msg['To'] = "recipient@example.com"
                msg['Subject'] = "Email Scan"
                if "<html" in raw_input.lower() or "<a " in raw_input.lower():
                    msg.set_content(raw_input, subtype='html')
                else:
                    msg.set_content(raw_input)
            return msg
        except Exception:
            msg = EmailMessage()
            msg['From'] = "sender@example.com"
            msg['To'] = "recipient@example.com"
            msg['Subject'] = "Email Scan"
            msg.set_content(raw_input)
            return msg

    def extract_red_flags(self, msg, feats_dict, urls):
        """Identifies human-readable security red flags based on features and content."""
        red_flags = []
        
        # 1. IP in URL
        if feats_dict.get('ipurls', 0) > 0:
            ip_urls = [u for u in urls if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", u)]
            red_flags.append({
                "severity": "CRITICAL",
                "title": "Raw IP Address in Hyperlink",
                "detail": f"Detected {feats_dict['ipurls']} URL(s) using numeric IP addresses instead of legitimate domain names ({', '.join(ip_urls[:2])}). Highly characteristic of malicious credential harvesters.",
                "feature": "ipurls"
            })

        # 2. Check domains mismatch
        if feats_dict.get('checkdomains', 1) == 0 and len(urls) > 0:
            sender_field = msg['From'] or msg['Return-Path'] or "unknown"
            red_flags.append({
                "severity": "HIGH",
                "title": "Sender & Target Domain Mismatch",
                "detail": f"Sender claims to be from '{sender_field}', but links direct the recipient to external, unaligned domain(s). Classic sign of brand impersonation.",
                "feature": "checkdomains"
            })

        # 3. Disguised Anchor Text (diffhref)
        if feats_dict.get('diffhref', 0) > 0:
            red_flags.append({
                "severity": "HIGH",
                "title": "Deceptive Hyperlink Display Text",
                "detail": f"Found {feats_dict['diffhref']} link(s) where displayed text disguises the actual destination URL (e.g. showing a trusted brand URL while redirecting elsewhere).",
                "feature": "diffhref"
            })

        # 4. Embedded Forms
        if feats_dict.get('forms', 0) > 0:
            red_flags.append({
                "severity": "CRITICAL",
                "title": "Interactive Data Harvesting Form Inside Email",
                "detail": f"Email body contains {feats_dict['forms']} HTML <form> element(s). Legitimate organizations almost never embed interactive input forms directly in emails.",
                "feature": "forms"
            })

        # 5. Embedded Scripts
        if feats_dict.get('scripts', 0) > 0:
            red_flags.append({
                "severity": "CRITICAL",
                "title": "Executable Scripts Detected",
                "detail": f"Found {feats_dict['scripts']} script tag(s). Executable JavaScript in emails is extremely dangerous and indicates an active exploit or tracker.",
                "feature": "scripts"
            })

        # 6. Urgent Phishing Trigger Words
        if feats_dict.get('badwords', 0) > 0:
            severity = "HIGH" if feats_dict['badwords'] >= 3 else "MEDIUM"
            red_flags.append({
                "severity": severity,
                "title": f"Social Engineering & Urgency Keywords ({feats_dict['badwords']} occurrences)",
                "detail": "Email uses pressure tactics and security buzzwords (e.g. 'verify', 'suspend', 'urgent', 'restrict', 'confirm') typical of psychological phishing traps.",
                "feature": "badwords"
            })

        # 7. Non-standard ports
        if feats_dict.get('nports', 0) > 0:
            red_flags.append({
                "severity": "HIGH",
                "title": "Non-Standard Port in URL",
                "detail": f"Hyperlinks connect to uncommon ports ({feats_dict['nports']} instance(s)), which frequently bypass standard corporate firewalls.",
                "feature": "nports"
            })

        # 8. Excessive Subdomains / Dots
        if feats_dict.get('ndots', 0) >= 4:
            red_flags.append({
                "severity": "MEDIUM",
                "title": "Suspicious URL Structure (Excessive Subdomains)",
                "detail": f"Max dots in a URL is {feats_dict['ndots']}. Attackers often use deeply nested subdomains to mimic legitimate brand names.",
                "feature": "ndots"
            })

        return red_flags

    def analyze_email(self, raw_input: str, sender: str = None, recipient: str = None, subject: str = None):
        """Full inference pipeline on single email."""
        msg = self.parse_input_to_email(raw_input, sender, recipient, subject)

        # Extract structural features
        raw_feats = [func(msg) for _, func in FEATURE_FUNCS]
        feats_dict = {name: val for (name, _), val in zip(FEATURE_FUNCS, raw_feats)}

        # Extract text & URLs
        extracted_text = clean_text(get_email_text(msg))
        urls = get_urls(msg)

        # Scale properties
        props_arr = np.array([raw_feats])
        props_scaled = self.scaler.transform(props_arr)

        # TF-IDF
        tfidf_vec = self.tfidf.transform([extracted_text])

        # Combined features
        comb_vec = hstack([tfidf_vec, props_scaled]).tocsr()

        # Run all 6 classifiers on TF-IDF + Properties
        classifier_names = [
            "Random Forest",
            "Gradient Boosting",
            "Logistic Regression",
            "Linear SVM",
            "Decision Tree",
            "Naive Bayes"
        ]

        model_results = []
        phishing_votes = 0
        prob_sum = 0.0

        for clf_name in classifier_names:
            model_key = f"TF-IDF + Properties__{clf_name}"
            clf = self.models.get(model_key)
            if clf is None:
                continue

            pred_class = int(clf.predict(comb_vec)[0])
            if pred_class == 1:
                phishing_votes += 1

            # Get probability or calibrated score
            if hasattr(clf, 'predict_proba'):
                prob = float(clf.predict_proba(comb_vec)[0][1])
            elif hasattr(clf, 'decision_function'):
                df_val = float(clf.decision_function(comb_vec)[0])
                # Sigmoid approx
                prob = float(1.0 / (1.0 + np.exp(-np.clip(df_val, -10, 10))))
            else:
                prob = float(pred_class)

            prob_sum += prob
            model_results.append({
                "classifier": clf_name,
                "prediction": "Phishing" if pred_class == 1 else "Legitimate",
                "is_phishing": bool(pred_class == 1),
                "confidence": round(prob if pred_class == 1 else (1.0 - prob), 4),
                "phishing_prob": round(prob, 4)
            })

        total_models = len(model_results)
        consensus_prob = (prob_sum / total_models) if total_models > 0 else 0.0
        consensus_percent = round(consensus_prob * 100, 1)

        # Primary verdict based on Random Forest / Gradient Boosting with consensus weighting
        primary_model = next((m for m in model_results if m['classifier'] == 'Random Forest'), model_results[0])
        is_overall_phishing = (phishing_votes >= (total_models / 2)) or (consensus_prob > 0.5)

        if consensus_percent >= 80:
            threat_level = "CRITICAL"
            badge_color = "#ef4444" # red
        elif consensus_percent >= 50:
            threat_level = "HIGH"
            badge_color = "#f97316" # orange
        elif consensus_percent >= 30:
            threat_level = "SUSPICIOUS"
            badge_color = "#eab308" # yellow
        elif consensus_percent >= 15:
            threat_level = "LOW RISK"
            badge_color = "#3b82f6" # blue
        else:
            threat_level = "SAFE"
            badge_color = "#10b981" # green

        # Red flags
        red_flags = self.extract_red_flags(msg, feats_dict, urls)

        # Feature explanation & status
        feature_breakdown = []
        feature_desc = {
            "nurls": ("Total URLs Found", "Number of distinct hyperlinks embedded in the email body or HTML."),
            "ndots": ("Max Dots in URLs", "Highest dot count in any URL. High dot count indicates obfuscated domain nesting."),
            "nports": ("Port Numbers in URLs", "Specific non-default network ports (e.g. :8080) attached to link destinations."),
            "nrecs": ("Distinct Recipients", "Number of unique To, Cc, Bcc recipients addressed."),
            "checkdomains": ("Domain Alignment", "1 if all link domains match the sender domain, 0 if links redirect elsewhere."),
            "nparts": ("MIME Parts", "Total MIME message parts (plain text, multipart, attachments)."),
            "hasHTML": ("Contains HTML", "Whether the email contains rendered HTML formatting (1=Yes, 0=No)."),
            "attachments": ("Attachments Count", "Number of attached payloads or downloadable files."),
            "badwords": ("Phishing Keywords", "Occurrences of urgent keywords: link, click, confirm, user, customer, suspend, verify, protect."),
            "ipurls": ("IP-Based URLs", "Number of URLs routing directly to a raw IP address instead of domain."),
            "diffhref": ("Mismatched Links", "Number of anchor tags where href target does not match visible anchor text."),
            "forms": ("Embedded Forms", "Number of interactive <form> tags present in the HTML."),
            "scripts": ("Embedded Scripts", "Number of <script> execution tags embedded in the message."),
            "encoding": ("Content Encoding", "MIME transfer encoding mode (base64, quoted-printable, etc.)."),
        }

        for fname, val in feats_dict.items():
            name_label, desc = feature_desc.get(fname, (fname, ""))
            is_suspicious = False
            if fname in ["ipurls", "diffhref", "forms", "scripts", "nports"] and val > 0:
                is_suspicious = True
            elif fname == "checkdomains" and val == 0 and feats_dict.get("nurls", 0) > 0:
                is_suspicious = True
            elif fname == "badwords" and val >= 2:
                is_suspicious = True
            elif fname == "ndots" and val >= 4:
                is_suspicious = True

            feature_breakdown.append({
                "key": fname,
                "label": name_label,
                "value": val,
                "description": desc,
                "is_suspicious": is_suspicious
            })

        # Phishing keywords found in text
        keywords = ['link', 'click', 'confirm', 'user', 'customer', 'client', 'suspend', 'restrict', 'verify', 'protect']
        found_keywords = [w for w in keywords if w in extracted_text.lower()]

        return {
            "verdict": "PHISHING" if is_overall_phishing else "LEGITIMATE",
            "is_phishing": is_overall_phishing,
            "threat_level": threat_level,
            "badge_color": badge_color,
            "risk_score": consensus_percent,
            "phishing_votes": phishing_votes,
            "total_models": total_models,
            "models_breakdown": model_results,
            "red_flags": red_flags,
            "features": feature_breakdown,
            "urls_detected": urls[:10],
            "phishing_keywords_found": found_keywords,
            "extracted_text_snippet": extracted_text[:400] + ("..." if len(extracted_text) > 400 else ""),
            "email_headers": {
                "From": msg['From'] or "None",
                "To": msg['To'] or "None",
                "Subject": msg['Subject'] or "None",
                "Content-Type": msg.get_content_type()
            }
        }

# Global singleton
predictor = EmailPredictor()

if __name__ == "__main__":
    test_mail = """From: support@secure-update-paypal.com
To: target@company.com
Subject: Action Required: Your Account has been suspended!

Dear customer, please click http://192.168.1.50/account to verify your details immediately and protect your funds."""
    res = predictor.analyze_email(test_mail)
    print("Verdict:", res["verdict"])
    print("Risk Score:", res["risk_score"])
    print("Threat Level:", res["threat_level"])
    print("Red Flags:", len(res["red_flags"]))
    print("Model Votes:", f"{res['phishing_votes']}/{res['total_models']}")
