"""
Simplified Phishing Email Classifier (scikit-learn version)
============================================================
This script replicates the core logic of the PySpark-based project
using scikit-learn, so it can run without Java/Spark/SparkNLP.

It reads the same .mbox email datasets, extracts the same features,
trains multiple classifiers, and reports performance metrics.
"""

import mailbox
import os
import re
import time
import warnings
import numpy as np
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, classification_report, roc_curve
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

import nltk
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

warnings.filterwarnings('ignore')

# ============================================================
# EMAIL PARSING UTILITIES (mirrors utils.py)
# ============================================================

def mbox_reader(stream):
    """Read a non-ascii message from mailbox."""
    data = stream.read()
    text = data.decode(encoding="latin-1")
    return mailbox.mboxMessage(text)


def get_payload_dict(msg, result=None):
    """Get all parts of an email as a list of dicts with mimeType and payload."""
    if result is None:
        result = []
    payload = msg.get_payload()
    if msg.get('content-transfer-encoding') == 'base64':
        payload = msg.get_payload(decode=True)
    if msg.is_multipart():
        for sub in payload:
            get_payload_dict(sub, result)
    else:
        result.append({"mimeType": msg.get_content_type(), "payload": payload})
    return result


def get_email_text(msg):
    """Extract all text content from an email, stripping HTML."""
    parts = get_payload_dict(msg)
    text = ""
    for part in parts:
        if 'text' in part['mimeType'] or 'multipart' in part['mimeType']:
            try:
                soup = BeautifulSoup(str(part['payload']), "lxml")
                for s in soup(["script", "style"]):
                    s.extract()
                clean = ' '.join(soup.stripped_strings)
                text += clean
            except:
                text += str(part['payload'])
    return text


def clean_text(text):
    """Clean email text: remove URLs, fix encoding artifacts."""
    text = text.replace('=\n', '')
    url_pattern = re.compile(r"https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    text = re.sub(url_pattern, 'url', text)
    return text


def is_empty(msg):
    """Check if an email is empty."""
    parts = get_payload_dict(msg)
    total = sum(len(re.sub(r'\s+', '', str(p['payload']))) for p in parts)
    return total < 1


# ============================================================
# FEATURE EXTRACTION (mirrors SpyderTest.py feature classes)
# ============================================================

def get_urls(msg):
    """Extract URLs from email."""
    text = msg.as_string().replace('=\n', '')
    regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    return re.findall(regex, text)


def feat_nurls(msg):
    return len(get_urls(msg))


def feat_ndots(msg):
    urls = get_urls(msg)
    return max((url.count('.') for url in urls), default=0)


def feat_nports(msg):
    urls = get_urls(msg)
    count = 0
    for url in urls:
        try:
            if urlparse(url).port:
                count += 1
        except:
            pass
    return count


def feat_nrecs(msg):
    recs = []
    for field in ['To', 'Cc', 'Bcc']:
        val = msg[field]
        if val:
            recs.extend(re.findall(r'[\w.-]+@[\w.-]+', val))
    return len(set(recs))


def feat_checkdomains(msg):
    sender_field = msg['From'] or msg['Return-Path'] or ""
    sender = re.findall(r'@[\w.\-]+', sender_field)
    if not sender:
        return 0
    sender_domain = sender[0][1:]
    urls = get_urls(msg)
    for url in urls:
        if url and sender_domain not in url:
            return 0
    return 1


def feat_nparts(msg):
    parts = 0
    for part in msg.walk():
        if 'multipart' not in part.get_content_type():
            parts += 1
    return parts


def feat_hashtml(msg):
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            return 1
    return 0


def feat_attachments(msg):
    count = 0
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            count += 1
    return count


def feat_badwords(msg):
    words = ['link', 'click', 'confirm', 'user', 'customer',
             'client', 'suspend', 'restrict', 'verify', 'protect']
    text = clean_text(get_email_text(msg)).lower()
    return sum(text.count(w) for w in words)


def feat_ipurls(msg):
    ip_regex = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    urls = get_urls(msg)
    ips = set()
    for url in urls:
        ips.update(re.findall(ip_regex, url))
    return len(ips)


def feat_diffhref(msg):
    try:
        soup = BeautifulSoup(msg.as_string(), 'lxml')
        count = 0
        for link in soup.find_all('a'):
            if link.get('href') != link.text:
                count += 1
        return count
    except:
        return 0


def feat_forms(msg):
    try:
        soup = BeautifulSoup(msg.as_string(), 'lxml')
        return len(soup.find_all('form'))
    except:
        return 0


def feat_scripts(msg):
    try:
        soup = BeautifulSoup(msg.as_string(), 'lxml')
        return len(soup.find_all('script'))
    except:
        return 0


def feat_encoding(msg):
    enc_map = {
        "quoted-printable": 1, "none": 2, "base64": 3, "utf-8": 4,
        "8bit": 5, "binary": 6, "7bit": 7
    }
    enc = msg.get("Content-Transfer-Encoding")
    if not enc:
        enc = 'none'
    enc = enc.lower()
    match = re.findall(r'[\w-]+', enc)
    enc = match[0] if match else 'none'
    return enc_map.get(enc, 8)


FEATURE_FUNCS = [
    ("nurls", feat_nurls),
    ("ndots", feat_ndots),
    ("nports", feat_nports),
    ("nrecs", feat_nrecs),
    ("checkdomains", feat_checkdomains),
    ("nparts", feat_nparts),
    ("hasHTML", feat_hashtml),
    ("attachments", feat_attachments),
    ("badwords", feat_badwords),
    ("ipurls", feat_ipurls),
    ("diffhref", feat_diffhref),
    ("forms", feat_forms),
    ("scripts", feat_scripts),
    ("encoding", feat_encoding),
]


# ============================================================
# DATA LOADING
# ============================================================

def load_mbox(filepath, label, limit=5000):
    """Load emails from an .mbox file, return list of (text, features, label)."""
    print(f"  [*] Loading: {os.path.basename(filepath)}", end="", flush=True)
    try:
        mbox = mailbox.mbox(filepath, factory=mbox_reader)
    except Exception as e:
        print(f" [ERROR] {e}")
        return []

    records = []
    count = 0
    for message in mbox:
        if count >= limit:
            break
        if is_empty(message):
            continue
        try:
            text = clean_text(get_email_text(message))
            feats = [func(message) for _, func in FEATURE_FUNCS]
            records.append((text, feats, label))
            count += 1
        except Exception:
            continue

    print(f" -> {count} emails loaded", flush=True)
    return records


def load_all_data(halflimit=500):
    """Load phishing and legitimate email datasets."""
    print("\n" + "=" * 60)
    print("LOADING EMAIL DATASETS")
    print("=" * 60, flush=True)

    all_records = []
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load phishing emails
    phishing_dir = os.path.join(base_dir, "phishing_datasets")
    print(f"\n[PHISHING] Phishing emails (limit: {halflimit}):", flush=True)
    remaining = halflimit
    if os.path.exists(phishing_dir):
        for f in sorted(os.listdir(phishing_dir)):
            if remaining <= 0:
                break
            fpath = os.path.join(phishing_dir, f)
            if os.path.isfile(fpath):
                records = load_mbox(fpath, label=1, limit=remaining)
                all_records.extend(records)
                remaining -= len(records)

    # Load legitimate emails
    legit_dir = os.path.join(base_dir, "legit_datasets")
    print(f"\n[LEGIT] Legitimate emails (limit: {halflimit}):", flush=True)
    remaining = halflimit
    if os.path.exists(legit_dir):
        for f in sorted(os.listdir(legit_dir)):
            if remaining <= 0:
                break
            fpath = os.path.join(legit_dir, f)
            if os.path.isfile(fpath):
                records = load_mbox(fpath, label=0, limit=remaining)
                all_records.extend(records)
                remaining -= len(records)

    phish_count = sum(1 for _, _, l in all_records if l == 1)
    legit_count = sum(1 for _, _, l in all_records if l == 0)
    print(f"\n[TOTAL] {len(all_records)} emails ({phish_count} phishing, {legit_count} legitimate)", flush=True)
    return all_records


# ============================================================
# MODEL TRAINING AND EVALUATION
# ============================================================

def train_and_evaluate(X_text, X_props, y, output_dir):
    """Train multiple classifiers and evaluate them."""

    print("\n" + "=" * 60)
    print("TRAINING & EVALUATING CLASSIFIERS")
    print("=" * 60, flush=True)

    # Split data
    X_text_train, X_text_test, X_props_train, X_props_test, y_train, y_test = \
        train_test_split(X_text, X_props, y, test_size=0.2, random_state=42, stratify=y)

    # Create TF-IDF features
    print("\n[*] Building TF-IDF features...", flush=True)
    tfidf = TfidfVectorizer(max_features=500, min_df=2)
    X_tfidf_train = tfidf.fit_transform(X_text_train)
    X_tfidf_test = tfidf.transform(X_text_test)

    # Combine TF-IDF + property features
    from scipy.sparse import hstack
    scaler = MinMaxScaler()
    X_props_train_scaled = scaler.fit_transform(X_props_train)
    X_props_test_scaled = scaler.transform(X_props_test)

    feature_sets = {
        "TF-IDF Only": (X_tfidf_train, X_tfidf_test),
        "Properties Only": (X_props_train_scaled, X_props_test_scaled),
        "TF-IDF + Properties": (
            hstack([X_tfidf_train, X_props_train_scaled]),
            hstack([X_tfidf_test, X_props_test_scaled])
        ),
    }

    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
        "Linear SVM": LinearSVC(max_iter=2000, random_state=42),
        "Naive Bayes": MultinomialNB(alpha=1.0),
    }

    results = []
    all_results_for_plot = {}

    for feat_name, (X_train, X_test) in feature_sets.items():
        print(f"\n{'=' * 50}")
        print(f"Feature Set: {feat_name}")
        print(f"{'=' * 50}", flush=True)
        all_results_for_plot[feat_name] = {}

        for clf_name, clf in classifiers.items():
            # Naive Bayes can't handle negative values, skip for property-only
            if clf_name == "Naive Bayes" and "Properties" in feat_name and "TF-IDF" not in feat_name:
                continue

            start = time.time()
            try:
                clf_copy = clf.__class__(**clf.get_params())
                clf_copy.fit(X_train, y_train)
                y_pred = clf_copy.predict(X_test)

                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, zero_division=0)
                rec = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                cm = confusion_matrix(y_test, y_pred)

                # AUC-ROC (need probability scores)
                try:
                    if hasattr(clf_copy, 'predict_proba'):
                        y_prob = clf_copy.predict_proba(X_test)[:, 1]
                    elif hasattr(clf_copy, 'decision_function'):
                        y_prob = clf_copy.decision_function(X_test)
                    else:
                        y_prob = y_pred.astype(float)
                    auc = roc_auc_score(y_test, y_prob)
                    all_results_for_plot[feat_name][clf_name] = (y_test, y_prob)
                except:
                    auc = 0.0

                elapsed = time.time() - start

                print(f"\n  [{clf_name}]")
                print(f"     Accuracy:  {acc:.4f}")
                print(f"     Precision: {prec:.4f}")
                print(f"     Recall:    {rec:.4f}")
                print(f"     F1-Score:  {f1:.4f}")
                print(f"     AUC-ROC:   {auc:.4f}")
                print(f"     Confusion Matrix: {cm.tolist()}")
                print(f"     Time: {elapsed:.2f}s", flush=True)

                results.append({
                    'features': feat_name,
                    'classifier': clf_name,
                    'accuracy': acc,
                    'precision': prec,
                    'recall': rec,
                    'f1': f1,
                    'auc_roc': auc,
                    'time': elapsed
                })

            except Exception as e:
                print(f"\n  [ERROR] {clf_name}: Failed -- {e}", flush=True)

    # Plot ROC curves
    plot_roc_curves(all_results_for_plot, output_dir)

    # Print summary table
    print_summary(results)

    return results


def plot_roc_curves(all_results, output_dir):
    """Plot ROC curves for all feature-classifier combinations."""
    for feat_name, clf_results in all_results.items():
        if not clf_results:
            continue
        plt.figure(figsize=(10, 7), dpi=100)
        plt.title(f'ROC Curve -- {feat_name}', fontsize=14, fontweight='bold')
        plt.xlabel('False Positive Rate (1 - Specificity)')
        plt.ylabel('True Positive Rate (Sensitivity)')

        for clf_name, (y_true, y_scores) in clf_results.items():
            try:
                fpr, tpr, _ = roc_curve(y_true, y_scores)
                auc_val = roc_auc_score(y_true, y_scores)
                plt.plot(fpr, tpr, label=f'{clf_name} (AUC={auc_val:.3f})', linewidth=2)
            except:
                pass

        plt.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Random')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        safe_name = feat_name.replace(' ', '_').replace('+', 'plus').lower()
        filepath = os.path.join(output_dir, f'roc_{safe_name}.png')
        plt.savefig(filepath)
        plt.close()
        print(f"\n[ROC] ROC curve saved: {filepath}", flush=True)


def print_summary(results):
    """Print a summary table of all results."""
    print("\n\n" + "=" * 90)
    print("RESULTS SUMMARY")
    print("=" * 90)
    print(f"{'Features':<22} {'Classifier':<22} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} {'AUC':>6} {'Time':>7}")
    print("-" * 90)

    results.sort(key=lambda x: x['f1'], reverse=True)
    for r in results:
        print(f"{r['features']:<22} {r['classifier']:<22} "
              f"{r['accuracy']:>6.3f} {r['precision']:>6.3f} {r['recall']:>6.3f} "
              f"{r['f1']:>6.3f} {r['auc_roc']:>6.3f} {r['time']:>6.1f}s")

    if results:
        best = results[0]
        print(f"\n[BEST] Best Combination: {best['features']} + {best['classifier']}")
        print(f"   F1-Score: {best['f1']:.4f} | Accuracy: {best['accuracy']:.4f} | AUC-ROC: {best['auc_roc']:.4f}", flush=True)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    start_time = time.time()

    print("=" * 60)
    print("  Phishing Email Classifier (scikit-learn version)")
    print("=" * 60, flush=True)

    # Configure: how many emails per class to load
    HALF_LIMIT = 500  # Set higher for better results (e.g., 2000), lower for speed

    # Load data
    records = load_all_data(halflimit=HALF_LIMIT)

    if len(records) < 10:
        print("\n[ERROR] Not enough emails loaded. Check that dataset files exist.")
        exit(1)

    # Prepare data
    texts = [r[0] for r in records]
    properties = np.array([r[1] for r in records])
    labels = np.array([r[2] for r in records])

    # Output directory for plots
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Train and evaluate
    results = train_and_evaluate(texts, properties, labels, output_dir)

    elapsed = (time.time() - start_time) / 60
    print(f"\n[TIME] Total time: {elapsed:.2f} minutes")
    print("\n[DONE] Check the ROC curve images in the project directory.", flush=True)
