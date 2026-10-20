"""
Pre-trains and saves the models and evaluation metrics for the Phishing Email Classification Frontend.
"""
import os
import time
import json
import joblib
import numpy as np
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve
)

from run_simple import load_all_data, FEATURE_FUNCS, clean_text, get_email_text

BUNDLE_PATH = os.path.join(os.path.dirname(__file__), "model_bundle.joblib")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "metrics_summary.json")

def train_and_save(half_limit=500):
    print(f"[*] Loading data (half_limit={half_limit})...")
    records = load_all_data(halflimit=half_limit)
    if len(records) < 10:
        raise ValueError("Not enough records loaded.")

    texts = [r[0] for r in records]
    properties = np.array([r[1] for r in records])
    labels = np.array([r[2] for r in records])

    X_text_train, X_text_test, X_props_train, X_props_test, y_train, y_test = \
        train_test_split(texts, properties, labels, test_size=0.2, random_state=42, stratify=labels)

    print("[*] Vectorizing text (TF-IDF)...")
    tfidf = TfidfVectorizer(max_features=500, min_df=2)
    X_tfidf_train = tfidf.fit_transform(X_text_train)
    X_tfidf_test = tfidf.transform(X_text_test)

    print("[*] Scaling property features...")
    scaler = MinMaxScaler()
    X_props_train_scaled = scaler.fit_transform(X_props_train)
    X_props_test_scaled = scaler.transform(X_props_test)

    # Hybrid features
    X_comb_train = hstack([X_tfidf_train, X_props_train_scaled]).tocsr()
    X_comb_test = hstack([X_tfidf_test, X_props_test_scaled]).tocsr()

    feature_splits = {
        "TF-IDF Only": (X_tfidf_train, X_tfidf_test),
        "Properties Only": (X_props_train_scaled, X_props_test_scaled),
        "TF-IDF + Properties": (X_comb_train, X_comb_test),
    }

    classifier_templates = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
        "Linear SVM": LinearSVC(max_iter=2000, random_state=42),
        "Naive Bayes": MultinomialNB(alpha=1.0),
    }

    benchmarks = []
    trained_models = {}  # for inference, we keep models trained on "TF-IDF + Properties" and individual sets
    roc_data = {}

    for feat_name, (X_tr, X_te) in feature_splits.items():
        roc_data[feat_name] = {}
        for clf_name, clf_proto in classifier_templates.items():
            if clf_name == "Naive Bayes" and "Properties" in feat_name and "TF-IDF" not in feat_name:
                continue

            t0 = time.time()
            clf = clf_proto.__class__(**clf_proto.get_params())
            clf.fit(X_tr, y_train)
            train_time = time.time() - t0

            y_pred = clf.predict(X_te)
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            cm = confusion_matrix(y_test, y_pred).tolist()

            try:
                if hasattr(clf, 'predict_proba'):
                    y_prob = clf.predict_proba(X_te)[:, 1]
                elif hasattr(clf, 'decision_function'):
                    df = clf.decision_function(X_te)
                    y_prob = (df - df.min()) / (df.max() - df.min() + 1e-9)
                else:
                    y_prob = y_pred.astype(float)
                auc = roc_auc_score(y_test, y_prob)

                fpr, tpr, _ = roc_curve(y_test, y_prob)
                # Sample 25 points for compact JSON storage
                step = max(1, len(fpr) // 25)
                roc_data[feat_name][clf_name] = {
                    "fpr": [float(x) for x in fpr[::step]],
                    "tpr": [float(x) for x in tpr[::step]],
                    "auc": float(auc)
                }
            except Exception as e:
                auc = 0.0

            benchmark_entry = {
                "features": feat_name,
                "classifier": clf_name,
                "accuracy": round(float(acc), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1": round(float(f1), 4),
                "auc_roc": round(float(auc), 4),
                "time_sec": round(float(train_time), 3),
                "confusion_matrix": cm
            }
            benchmarks.append(benchmark_entry)

            # Store models for production inference (specifically TF-IDF + Properties)
            model_key = f"{feat_name}__{clf_name}"
            trained_models[model_key] = clf

    # Extract Feature Importances from Random Forest on TF-IDF + Properties
    rf_comb = trained_models.get("TF-IDF + Properties__Random Forest")
    feature_importances = []
    if rf_comb is not None and hasattr(rf_comb, "feature_importances_"):
        prop_names = [name for name, _ in FEATURE_FUNCS]
        tfidf_names = [f"word: {w}" for w in tfidf.get_feature_names_out()]
        all_feat_names = tfidf_names + prop_names
        importances = rf_comb.feature_importances_
        # Top 15 features
        top_idx = np.argsort(importances)[::-1][:15]
        for idx in top_idx:
            feature_importances.append({
                "feature": all_feat_names[idx],
                "importance": round(float(importances[idx]), 4),
                "is_structural": idx >= len(tfidf_names)
            })

    dataset_stats = {
        "total_emails": len(records),
        "phishing_count": int(np.sum(labels == 1)),
        "legit_count": int(np.sum(labels == 0)),
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "tfidf_vocab_size": len(tfidf.get_feature_names_out()),
        "property_feature_count": len(FEATURE_FUNCS),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    bundle = {
        "tfidf": tfidf,
        "scaler": scaler,
        "models": trained_models,
        "benchmarks": benchmarks,
        "roc_data": roc_data,
        "dataset_stats": dataset_stats,
        "feature_importances": feature_importances,
        "feature_names": [name for name, _ in FEATURE_FUNCS]
    }

    print(f"[*] Saving model bundle to {BUNDLE_PATH}...")
    joblib.dump(bundle, BUNDLE_PATH, compress=3)

    print(f"[*] Saving metrics summary to {METRICS_PATH}...")
    metrics_summary = {
        "dataset_stats": dataset_stats,
        "benchmarks": benchmarks,
        "roc_data": roc_data,
        "feature_importances": feature_importances
    }
    def np_converter(o):
        if isinstance(o, (np.bool_, np.generic)):
            return o.item()
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2, default=np_converter)

    print("[+] Training and bundling complete!")
    return bundle

if __name__ == "__main__":
    train_and_save(half_limit=400)
