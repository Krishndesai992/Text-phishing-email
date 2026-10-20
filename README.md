# PhishShield AI — Phishing Email ML Detection & Threat Intelligence

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E.svg)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-success.svg)](tests/)

> An end-to-end cybersecurity threat intelligence system combining Natural Language Processing (TF-IDF N-Grams) and 14 structural email forensic heuristics to classify suspicious emails using an ensemble of 6 machine learning models.

---

## ⚡ Quick Start (Under 1 Minute)

### On Windows
If Python is installed, double-click **`run_frontend.bat`** or run:
```powershell
python run_frontend.py
```
Your default browser will automatically launch: **`http://127.0.0.1:8050`**

### With Docker
```bash
docker compose up --build
```
Access the dashboard at **`http://localhost:8050`**.

---

## 📋 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation & Setup](#-installation--setup)
3. [How to Run](#-how-to-run)
   - [Option A: Web Dashboard (Recommended)](#option-a-interactive-web-dashboard-recommended)
   - [Option B: Command-Line ML Evaluation](#option-b-standalone-ml-training--evaluation-run_simplepy)
   - [Option C: Retraining the Model Bundle](#option-c-retrain--update-cached-models-train_and_cachepy)
   - [Option D: Docker Deployment](#option-d-docker-containerization-dockerfile--compose)
   - [Option E: PySpark Big Data Pipeline](#option-e-pyspark-pipeline-spydertestpy-optional)
4. [Testing & Verification](#-testing--verification)
5. [Project Structure](#-project-structure)
6. [How It Works](#-how-it-works)
7. [Datasets](#-datasets)
8. [Documentation Links](#-documentation-links)
9. [Troubleshooting & FAQ](#-troubleshooting--faq)
10. [License](#-license)

---

## 💻 Prerequisites

- **Python**: Version `3.9`, `3.10`, or `3.11` recommended.
- **Git** (to clone the repository).
- *(Optional)* **Docker** & **Docker Compose** (for containerized deployment).
- *(Optional)* **Java 8 or 11 JDK** (only required if running the legacy PySpark pipeline `SpyderTest.py`).

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Text_Phishing_Email_ML_Classification
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Optional)* Pre-download NLTK corpora (they will also automatically download on first run):
```bash
python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('omw-1.4')"
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

## 🚀 How to Run

### Option A: Interactive Web Dashboard (Recommended)
Launch the full web dashboard with the live Email Forensic Inspector:

```bash
python run_frontend.py
```
*(Or on Windows, simply double-click `run_frontend.bat`)*

- Open your browser at: **`http://localhost:8050`** or **`http://127.0.0.1:8050`**
- **Dashboard Features**:
  - **Live Composer**: Compose or paste any suspicious email subject, sender, and body.
  - **Raw RFC-822 Inspector**: Inspect raw email headers, MIME payloads, and transfer encoding.
  - **File Uploader**: Drag and drop `.eml`, `.txt`, `.msg`, or `.mbox` files directly.
  - **Ensemble Consensus**: Simultaneous risk probability across 6 classifiers (Random Forest, Gradient Boosting, Logistic Regression, Linear SVM, Decision Tree, Naive Bayes).
  - **Forensic Signals**: Highlights malicious urgency keywords, extracts destination links, and flags anchor discrepancies (`diffhref`).
  - **In-App Retraining**: Retrain classifiers with custom sample sizes right from the browser.

---

### Option B: Standalone ML Training & Evaluation (`run_simple.py`)
Run the pure scikit-learn training, evaluation, and benchmark script directly in your terminal:

```bash
python run_simple.py
```

- Reads emails from `phishing_datasets/` and `legit_datasets/`.
- Trains and evaluates **6 ML algorithms** across **3 feature architectures**:
  1. TF-IDF Text N-Grams Only
  2. Structural Email Heuristic Properties Only
  3. Hybrid Fusion (TF-IDF + Properties)
- Outputs accuracy, precision, recall, F1-score, AUC-ROC, confusion matrices, and ROC curve plots (`roc_*.png`).

---

### Option C: Retrain & Update Cached Models (`train_and_cache.py`)
To regenerate the serialized model bundle used by the web application:

```bash
python train_and_cache.py
```

- Fits vectorizer, feature scalers, and all 6 models on the email corpus.
- Exports the pre-computed bundle to `model_bundle.joblib`.
- Exports metrics benchmarks to `metrics_summary.json`.

---

### Option D: Docker Containerization (`Dockerfile` & `compose`)
Deploy seamlessly using Docker:

```bash
# Build and run
docker compose up -d --build

# Follow logs
docker compose logs -f

# Stop container
docker compose down
```

---

### Option E: PySpark Big Data Pipeline (`SpyderTest.py`) *(Optional / Big Data)*
If you want to run the original Apache Spark MLlib / Spark-NLP distributed classification pipeline:

```bash
python SpyderTest.py
```
> **Note**: Requires an active Apache Spark installation, Spark-NLP (`sparknlp`), and a compatible Java JDK (8 or 11) in `JAVA_HOME`.

---

## 🧪 Testing & Verification

Run the automated test suite covering feature extraction, inference engine consensus, and REST endpoints:

```bash
python -m unittest discover tests -v
```

All 13 unit and integration tests execute in < 0.2s without requiring external network connectivity.

---

## 📁 Project Structure

```text
Text_Phishing_Email_ML_Classification/
├── docs/                           # Long-form technical documentation
│   ├── ARCHITECTURE.md             # In-depth system architecture & ML specifications
│   ├── DEPLOYMENT.md               # Production deployment, Nginx, Systemd & Cloud Run guide
│   └── figures/                    # Architectural diagrams, DFDs & UI previews
├── static/                         # Web frontend static assets
│   ├── css/
│   │   └── style.css               # Cybersecurity dark-theme UI styling
│   ├── images/                     # Web brand assets (logo, favicon)
│   ├── js/
│   │   └── app.js                  # Frontend state management & live API client
│   └── index.html                  # Email Forensic Inspector Single-Page App
├── legit_datasets/                 # Legitimate sample mbox email corpora (Enron)
├── phishing_datasets/              # Phishing email mbox corpora (Jose Nazario corpus)
├── scripts/                        # Maintenance, report & dataset utility scripts
│   ├── enron2mbox.py               # Maildir to Mbox conversion utility
│   ├── gen_report.py               # Project report document generator
│   └── make_diagrams.py            # Architecture and DFD diagram generator
├── tests/                          # Automated test suite (Python unittest)
│   ├── __init__.py
│   ├── test_features.py            # Unit tests for text cleaning and 14 heuristics
│   ├── test_predictor.py           # Unit tests for EmailPredictor inference engine
│   └── test_server.py              # Integration tests for FastAPI endpoint handlers
├── predictor.py                    # Inference engine & email feature extraction logic
├── server.py                       # FastAPI REST backend serving predictions & static UI
├── run_frontend.py                 # Convenience launcher script (opens browser at port 8050)
├── run_frontend.bat                # 1-click Windows batch launcher
├── run_simple.py                   # Standalone scikit-learn training & evaluation script
├── train_and_cache.py              # Script to train and update model_bundle.joblib
├── metrics_summary.json            # Cached evaluation benchmarks & metrics
├── requirements.txt                # Production package dependencies
├── requirements-dev.txt            # Development and testing dependencies
├── samples.py                      # Email samples dictionary
├── utils.py                        # Helper utilities for email parsing
├── MLModeler.py                    # Legacy Spark ML pipeline modeling helpers
├── SpyderTest.py                   # Legacy PySpark / Spark-NLP pipeline script
├── Dockerfile                      # Production Docker container definition
├── docker-compose.yml              # One-command Docker Compose orchestration
├── .env.example                    # Template environment variables
├── .gitignore                      # Comprehensive Git exclusion rules
├── LICENSE                         # GNU General Public License v3.0
└── README.md                       # Primary repository documentation
```

---

## 🧠 How It Works

1. **Email Ingestion**: Ingests headers (`From`, `To`, `Subject`), MIME parts, plain text, and HTML payloads.
2. **Dual-Branch Feature Extraction**:
   - **Branch 1 (NLP TF-IDF)**: Cleans text (stopword elimination, lemmatization) and extracts top 500 n-gram tokens.
   - **Branch 2 (Structural Properties)**: Computes 14 security signals (URL count, domain alignment, mismatched hyperlinks `diffhref`, IP-based URLs, HTML forms, script tags, urgency trigger words).
3. **Feature Space Fusion**: Normalizes numeric features and concatenates with sparse TF-IDF vectors into a unified feature representation.
4. **Ensemble Consensus**: Evaluates parallel predictions from 6 classifiers to produce a consensus risk score, threat level (`CRITICAL`, `HIGH`, `SUSPICIOUS`, `LOW RISK`, `SAFE`), and human-readable red flags.

---

## 📊 Datasets

The project uses standard cyber-forensic benchmark email corpora stored in Mbox format:
- **Phishing Emails**: Sourced from the public *Jose Nazario Phishing Corpus*.
- **Legitimate Emails**: Sourced from the *Enron Email Corpus*.

You can add additional `.mbox` files into `phishing_datasets/` or `legit_datasets/` and run `python train_and_cache.py` to retrain with new data.

---

## 📚 Documentation Links

- [System Architecture & ML Specifications](docs/ARCHITECTURE.md)
- [Production Deployment Guide](docs/DEPLOYMENT.md)

---

## ❓ Troubleshooting & FAQ

### Port 8050 is already in use
Specify an alternate port via the `PORT` environment variable:
```powershell
$env:PORT="8080"; python run_frontend.py
```
Or on Linux/macOS:
```bash
PORT=8080 python run_frontend.py
```

### NLTK LookupError: Resource not found
If you encounter an NLTK error regarding missing corpora, run:
```bash
python -c "import nltk; nltk.download('all-corpora')"
```

### Initial Run: Model bundle auto-generation
If `model_bundle.joblib` is not present, the predictor will automatically run initial training on launch and save the bundle.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.
