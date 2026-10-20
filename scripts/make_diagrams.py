import os
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "figures"))
os.makedirs(BASE, exist_ok=True)

STYLE = """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{margin:0;padding:30px;background:#ffffff;color:#111;font-family:'Segoe UI',Arial,sans-serif;}
.wrap{background:#fff;}
.box{background:#eef4fb;border:2px solid #35618f;border-radius:10px;padding:14px 18px;font-size:15px;font-weight:600;text-align:center;}
.small{font-size:12px;font-weight:400;display:block;color:#333;}
.box.ellipse{border-radius:40px;background:#f7f9fc;}
.row{display:flex;justify-content:center;align-items:center;}
.vrow{display:flex;flex-direction:column;align-items:center;}
.arrow{font-size:26px;color:#35618f;font-weight:700;margin:6px 0;}
.varrow{display:block;text-align:center;font-size:22px;color:#35618f;margin:2px 0;}
.lbl{font-size:12px;color:#444;transform:rotate(0deg);}
h3.t{font-size:18px;text-align:center;margin:0 0 16px;}
.lane{display:flex;gap:26px;align-items:center;justify-content:center;}
.actor{font-size:60px;line-height:1;}
</style></head><body><div class="wrap">%s</div></body></html>
"""

diagrams = {}

# ---------------- Figure 3.1 Use-case ----------------
ucs = ["Scan Single Email", "Inspect Raw RFC-822 Email", "Upload .eml / .mbox File",
       "View Threat Assessment & Red Flags", "View Multi-Model Consensus",
       "View Model Benchmarks & ROC Curves", "Batch Analyse Email Set", "Retrain Models In-App"]
cells = "".join(f'<div class="box ellipse">{u}</div><div class="varrow">&#8618;</div>' for u in ucs)
diagrams["fig3_1_usecase"] = """
<h3 class="t">Use-Case Diagram</h3>
<div class="lane">
  <div class="vrow">
    <div class="actor">&#128100;</div>
    <div class="box">Actor:<span class="small">End User / Security Analyst</span></div>
  </div>
  <div style="font-size:34px;color:#35618f;font-weight:700;">&#8594;</div>
  <div class="vrow">%s</div>
</div>
<div class="varrow">&#8617;</div>
<div style="text-align:center;font-size:13px;color:#444;">System PhishShield &mdash; Phishing Email ML Detection &amp; Threat Intelligence (all use cases are read-only except Retrain Models)</div>
""" % cells

# ---------------- Figure 4.1 Activity ----------------
acts = ["Start", "Load trained model bundle (model_bundle.joblib)",
        "User submits email (Compose / Raw RFC-822 / Upload)",
        "Parse headers, MIME parts, HTML and plain text",
        "Extract 14 structural properties + extract text",
        "Vectorise text with TF-IDF; scale properties",
        "Run 6 classifiers in parallel",
        "Aggregate consensus, risk score and red flags",
        "Render threat assessment on dashboard",
        "User satisfied? (No &rarr; Retrain in-app loop)",
        "End"]
flow = ""
for i, a in enumerate(acts):
    shape = "ellipse" if a in ("Start", "End") else ""
    flow += f'<div class="box {shape}" style="width:520px;">{a}</div>'
    if i < len(acts)-1:
        flow += '<div class="varrow">&#8595;</div>'
diagrams["fig4_1_activity"] = "<h3 class='t'>Activity Diagram of a Scanning Session</h3>" + \
    "<div class='vrow'>" + flow + "</div>"

# ---------------- DFD Level 0 ----------------
diagrams["fig4_2_dfd0"] = """
<h3 class="t">Data Flow Diagram &mdash; Level 0 (Context)</h3>
<div class="lane">
  <div class="vrow" style="width:240px;">
    <div class="box">Email Data Sources<span class="small">Phishing corpus mbox (Nazario)</span><span class="small">Legitimate corpus mbox (Enron)</span></div>
    <div class="arrow">&#8594;</div>
  </div>
  <div class="vrow" style="width:300px;">
    <div class="box" style="background:#dde9f7;">0<span class="small" style="font-weight:700;">PhishShield Email<br>Classification System</span><span class="small">Parses, vectorises, classifies and&nbsp;assesses</span></div>
  </div>
  <div class="vrow" style="width:240px;">
    <div class="arrow">&#8594;</div>
    <div class="box">User (Browser)<span class="small">Verdict, risk score, red flags,<br>model consensus, metrics</span></div>
  </div>
</div>
<div style="text-align:center;margin-top:10px;" class="lbl">&#8630; Single email / batch requests also flow from the User into the system (API endpoints /api/analyze, /api/batch-analyze)</div>
"""

# ---------------- DFD Level 1 ----------------
nodes = [("1", "Data Loading<br><span class='small'>mbox parser<br>phishing/legit corpora</span>"),
         ("2", "Text Cleaning<br><span class='small'>tokenise, stopword<br>removal, lemmatise</span>"),
         ("3", "Feature Extraction<br><span class='small'>TF-IDF n-grams (500)<br>14 structural props</span>"),
         ("4", "Model Training<br><span class='small'>6 classifiers<br>80/20 stratified split</span>"),
         ("5", "Model Bundle<br><span class='small'>model_bundle.joblib<br>metrics_summary.json</span>"),
         ("6", "Inference Engine<br><span class='small'>consensus, risk,<br>red flags</span>"),
         ("7", "REST API<br><span class='small'>FastAPI endpoints</span>"),
         ("8", "Web Dashboard<br><span class='small'>single-page UI<br>port 8050</span>")]
flow1 = ""
for i, (n, t) in enumerate(nodes):
    flow1 += f'<div class="box" style="min-width:150px;"><span style="font-size:11px;color:#35618f;">{n}</span><br>{t}</div>'
    if i < len(nodes)-1:
        flow1 += '<div class="arrow">&#8594;</div>'
flow2 = ""
for i, (n, t) in enumerate(nodes[::-1]):
    flow2 += f'<div class="box" style="min-width:150px;"><span style="font-size:11px;color:#35618f;">{n}</span><br>{t}</div>'
    if i < len(nodes)-1:
        flow2 += '<div class="arrow">&#8594;</div>'
diagrams["fig4_3_dfd1"] = """
<h3 class="t">Data Flow Diagram &mdash; Level 1</h3>
<div class="vrow"><b style="font-size:13px;">Training (offline):</b></div>
<div class="row" style="gap:8px;">%s</div>
<div style="text-align:center;" class="varrow">&#8595;</div>
<div class="vrow"><b style="font-size:13px;">Inference (on request):</b></div>
<div class="row" style="gap:8px;">%s</div>
""" % (flow1, flow2)

# ---------------- Architecture ----------------
layers = [("Presentation Layer", "Single-page dashboard: Email Composer &middot; RFC-822 Inspector &middot; File Uploader &middot; Threat Assessment Panel &middot; Benchmark Charts (static/index.html, app.js, style.css)"),
          ("Serving Layer", "FastAPI REST API (server.py): /api/analyze &middot; /api/batch-analyze &middot; /api/status &middot; /api/samples &middot; /api/retrain &nbsp;&mdash;&nbsp; served by Uvicorn on port 8050"),
          ("Inference Layer", "EmailPredictor (predictor.py): RFC-822/MIME parsing &middot; feature extraction &middot; TF-IDF vectorisation &middot; scaler &middot; ensemble consensus &middot; red-flag reasoning"),
          ("Machine Learning Layer", "Training pipeline (run_simple.py, train_and_cache.py): 6 classifiers (Random Forest, Gradient Boosting, Logistic Regression, Linear SVM, Decision Tree, Naive Bayes) &times; 3 feature architectures (TF-IDF / Properties / Hybrid) &middot; benchmarking &middot; ROC curves"),
          ("Feature Layer", "TF-IDF text n-grams (500 features, min_df=2) &middot; 14 structural email properties (nurls, ndots, diffhref, ipurls, forms, scripts, badwords, encoding, ...) normalised by Min-Max scaler"),
          ("Data Layer", "Phishing corpus mbox files (phishing_datasets/) &middot; legitimate corpus mbox files (legit_datasets/) &middot; cached artefacts: model_bundle.joblib &middot; metrics_summary.json")]
lay = "<div class='vrow'>"
lay += '<div style="font-size:13px;font-weight:700;color:#35618f;">User (Browser)</div><div class="arrow">&#8595;</div>'
for title, desc in layers:
    lay += f'<div class="box" style="width:860px;"><b>{title}</b><span class="small">{desc}</span></div><div class="arrow">&#8595;</div>'
lay += '<div style="font-size:13px;font-weight:700;color:#35618f;">Email Corpora / Cached Model</div></div>'
diagrams["fig5_1_architecture"] = "<h3 class='t'>System Architecture</h3>" + lay

for name, body in diagrams.items():
    with open(os.path.join(BASE, name + "_src.html" if False else name + ".src.html"), "w", encoding="utf-8") as f:
        f.write(STYLE % body)
print("wrote", len(diagrams), "diagram HTML files")
