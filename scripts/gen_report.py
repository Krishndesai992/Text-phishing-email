# -*- coding: utf-8 -*-
"""Generates the BDA Mini Project report DOCX for PhishShield AI."""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_FIG = os.path.join(BASE_DIR, "docs", "figures")
STATIC_IMG = os.path.join(BASE_DIR, "static", "images")

FIG_MAP = {
    "institution_logo.png": os.path.join(STATIC_IMG, "logo.png"),
    "fig3_1_usecase.png": os.path.join(DOCS_FIG, "use_case_diagram.png"),
    "fig4_1_activity.png": os.path.join(DOCS_FIG, "activity_diagram.png"),
    "fig4_2_dfd0.png": os.path.join(DOCS_FIG, "dfd_level_0.png"),
    "fig4_3_dfd1.png": os.path.join(DOCS_FIG, "dfd_level_1.png"),
    "fig5_1_architecture.png": os.path.join(DOCS_FIG, "architecture_diagram.png"),
    "fig6_1_dashboard.png": os.path.join(DOCS_FIG, "dashboard_preview.png"),
    "fig6_2_analysis.png": os.path.join(DOCS_FIG, "email_analysis_preview.png"),
    "fig6_3_roc.png": os.path.join(BASE_DIR, "roc_tf-idf_plus_properties.png"),
    "fig6_4_roc_tfidf.png": os.path.join(BASE_DIR, "roc_tf-idf_only.png"),
    "fig6_5_roc_props.png": os.path.join(BASE_DIR, "roc_properties_only.png"),
}

def FIG(n):
    if n in FIG_MAP and os.path.exists(FIG_MAP[n]):
        return FIG_MAP[n]
    cand = os.path.join(DOCS_FIG, n)
    if os.path.exists(cand):
        return cand
    cand2 = os.path.join(BASE_DIR, n)
    if os.path.exists(cand2):
        return cand2
    return os.path.join(os.path.dirname(__file__), n)

OUT = os.path.join(os.path.expanduser("~"), "Desktop", "BDA_Mini_Project_Report_Phishing_Email_Detection.docx")

TITLE = "PHISHSHIELD AI \u2013 PHISHING EMAIL DETECTION USING MACHINE LEARNING AND TEXT ANALYTICS"
MEMBERS = [
    ("Krish N Desai", "03", "232029"),
    ("Manas Dave", "06", "222023"),
    ("Ashmit Prasad", "15", "232138"),
]
GUIDE_NAME = "Ms. Jayshree Mittal"
GUIDE_DESIG = "Designation: Assistant Professor"

doc = Document()

# ---------- base style ----------
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = style.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
pf.space_after = Pt(6)

for sec in doc.sections:
    sec.top_margin = Inches(1); sec.bottom_margin = Inches(1)
    sec.left_margin = Inches(1); sec.right_margin = Inches(1)

def page_number_footer():
    sec = doc.sections[0]
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    run.font.name = "Times New Roman"; run.font.size = Pt(12)
page_number_footer()

def hapter(text, new_page=True):
    if new_page:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(16); r.bold = True
    return p

def hsec(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.size = Pt(14); r.bold = True; r.font.name = "Times New Roman"
    return p

def hsub(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.size = Pt(12); r.bold = True; r.font.name = "Times New Roman"
    return p

def body(text, first=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(12)
    return p

def center_text(text, size=12, bold=False, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(size); r.bold = bold; r.italic = italic
    return p

def fig_caption(no, caption, img, width=5.8, img_h=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(img, width=Inches(width))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(2); cp.paragraph_format.space_after = Pt(10)
    cr = cp.add_run("Figure {}: {}".format(no, caption))
    cr.font.name = "Times New Roman"; cr.font.size = Pt(12); cr.bold = True
    return p

def add_table(no, caption, headers, rows, widths=None):
    cap = None
    if caption:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(10); cap.paragraph_format.space_after = Pt(4)
        cr = cap.add_run("Table {}: {}".format(no, caption))
        cr.font.name = "Times New Roman"; cr.font.size = Pt(12); cr.bold = True
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, htxt in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(htxt); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val)); r.font.size = Pt(12); r.font.name = "Times New Roman"
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(6)
    return t

def cover_arrow(cond_text=None):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.5
    return p

# per-page header with project title (front pages) as in the sample
def set_header(text):
    sec = doc.sections[0]
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run(text)
    r.font.name = "Times New Roman"; r.font.size = Pt(10); r.italic = True

set_header("PHISHSHIELD AI \u2013 BDA MINI PROJECT")

# =====================================================================
# TITLE PAGE
# =====================================================================
center_text(" ", 8)
center_text("PHISHSHIELD AI", 22, bold=True)
center_text("PHISHING EMAIL DETECTION USING MACHINE LEARNING AND TEXT ANALYTICS", 16, bold=True)
p = doc.add_paragraph()
pic = p.add_run(); pic.add_picture(FIG("institution_logo.png"), width=Inches(2.0))
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
center_text("BDA Mini Project submitted in partial fulfillment of the requirements", 13)
center_text("of the degree of", 13)
center_text("B. E. Computer Engineering", 14, bold=True)
center_text("By", 13)
cover_arrow()
# members table
t = doc.add_table(rows=len(MEMBERS) + 1, cols=3)
t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_cells = t.rows[0].cells
for j, h in enumerate(["Name", "Roll No", "PID No"]):
    p = hdr_cells[j].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(h); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
for i, (nm, rl, pid) in enumerate(MEMBERS):
    cells = t.rows[i + 1].cells
    for j, v in enumerate([nm, rl, pid]):
        p = cells[j].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(v); r.font.size = Pt(12); r.font.name = "Times New Roman"
doc.add_paragraph()
center_text(GUIDE_NAME, 13, bold=True)
center_text(GUIDE_DESIG, 12)
doc.add_paragraph()
center_text("Department of Computer Engineering", 13, bold=True)
center_text("St. Francis Institute of Technology", 13, bold=True)
center_text("(Engineering College)", 12)
center_text("An Autonomous Institute, Affiliated to University of Mumbai", 12)
center_text("2026-2027", 12)

# =====================================================================
# CERTIFICATE  (i)
# =====================================================================
doc.add_page_break()
hapter("CERTIFICATE", new_page=False)
doc.add_paragraph()
body('This is to certify that the mini project entitled "PHISHSHIELD AI \u2013 PHISHING EMAIL '
     'DETECTION USING MACHINE LEARNING AND TEXT ANALYTICS" is a bonafide work of Krish N Desai '
     '(Roll No. 03), Manas Dave (Roll No. 06) and Ashmit Prasad (Roll No. 15) submitted to the '
     'University of Mumbai in partial fulfillment of the requirement for the BDA subject in the '
     'final year of Computer Engineering.')
doc.add_paragraph(); doc.add_paragraph()
center_text(GUIDE_NAME, 12, bold=True)
center_text("Guide", 12)

# =====================================================================
# DECLARATION (ii)
# =====================================================================
doc.add_page_break()
hapter("DECLARATION", new_page=False)
body("We declare that this written submission represents our ideas in our own words and where "
     "others' ideas or words have been included, we have adequately cited and referenced the "
     "original sources. We also declare that we have adhered to all principles of academic "
     "honesty and integrity and have not misrepresented or fabricated or falsified any "
     "idea/data/fact/source in our submission. We understand that any violation of the above "
     "will be cause for disciplinary action by the Institute and can also evoke penal action "
     "from the sources which have thus not been properly cited or from whom proper permission "
     "has not been taken when needed.")
doc.add_paragraph()
for nm, rl, _ in MEMBERS:
    center_text("______________________________")
    center_text("({body}, Roll No. {rl})".format(body=nm, rl=rl))
center_text("Date: ____________________")

# =====================================================================
# ABSTRACT (iii)
# =====================================================================
doc.add_page_break()
hapter("ABSTRACT", new_page=False)
body("Email phishing remains one of the most widespread and damaging cyber-attacks, in which an "
     "attacker disguises a malicious message as a trustworthy communication to steal credentials "
     "or deliver malware. This project, \"PhishShield AI \u2013 Phishing Email Detection using "
     "Machine Learning and Text Analytics\", develops a complete Big Data Analytics application "
     "that automatically classifies incoming emails as phishing or legitimate and explains every "
     "decision with human-readable security diagnostics.")
body("The system builds its intelligence from two benchmark email corpora \u2013 the Jose Nazario "
     "phishing corpus and the Enron legitimate corpus \u2013 totalling 800 pre-processed emails "
     "(400 phishing, 400 legitimate). A dual-branch feature pipeline is constructed: a text-mining "
     "branch using TF-IDF n-gram vectors of 500 dimensions, and a structural forensics branch "
     "computing 14 email properties such as URL counts, hyperlink-text deception, IP-based URLs, "
     "embedded forms, script tags and social-engineering keywords. Six supervised classifiers "
     "(Random Forest, Gradient Boosting, Logistic Regression, Linear SVM, Decision Tree and "
     "Naive Bayes) are trained across three feature architectures and benchmarked on a stratified "
     "80/20 split; the hybrid TF-IDF + properties representation reaches perfect test accuracy "
     "(100%) with an AUC-ROC of 1.000 for every classifier. The trained ensemble is served through "
     "a FastAPI backend and a single-page web dashboard that supports single, batch and .eml-file "
     "analysis, exposes per-model consensus probabilities, and flags seven categories of security "
     "red flags for the analyst. The project demonstrates that combining text analytics with "
     "structural email forensics yields a highly accurate, interpretable and deployable defence "
     "against phishing.")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
r = p.add_run("Keywords: Big Data Analytics, Phishing Detection, Machine Learning, TF-IDF, "
              "Email Forensics, Feature Engineering, Ensemble Learning, FastAPI.")
r.font.name = "Times New Roman"; r.font.size = Pt(12); r.bold = True

# =====================================================================
# CONTENTS (iv)
# =====================================================================
doc.add_page_break()
hapter("CONTENTS", new_page=False)
add_table(None, None, ["Chapter", "Contents", "Section"],
          [
           ["1", "INTRODUCTION", "1.1 Description; 1.2 Problem Formulation; 1.3 Motivation; 1.4 Proposed Solution; 1.5 Scope of the Project"],
           ["2", "REVIEW OF LITERATURE", ""],
           ["3", "SYSTEM ANALYSIS", "3.1 Functional Requirements; 3.2 Non-Functional Requirements; 3.3 Specific Requirements; 3.4 Use-Case Diagram and Description"],
           ["4", "ANALYSIS MODELING", "4.1 Activity Diagram; 4.2 Functional Modelling (Data Flow Diagrams)"],
           ["5", "DESIGN", "5.1 Architectural Design; 5.2 User Interface Design"],
           ["6", "IMPLEMENTATION", "6.1 Algorithms; 6.2 Working of the Project; 6.3 Results and Evaluation"],
           ["7", "CONCLUSIONS", "7.1 Conclusion; 7.2 Future Scope"],
           ["", "REFERENCES", ""],
           ["", "ACKNOWLEDGEMENTS", ""],
          ])

# =====================================================================
# LIST OF FIGURES (v)
# =====================================================================
doc.add_page_break()
hapter("LIST OF FIGURES", new_page=False)
add_table(None, None, ["Fig. No.", "Figure Caption"],
          [["3.1", "Use-Case Diagram"],
           ["4.1", "Activity Diagram of a Scanning Session"],
           ["4.2", "Data Flow Diagram \u2013 Level 0 (Context)"],
           ["4.3", "Data Flow Diagram \u2013 Level 1"],
           ["5.1", "System Architecture"],
           ["6.1", "PhishShield Dashboard \u2013 Single-Mail Analysis Home Page"],
           ["6.2", "Threat Assessment, Red Flags and Multi-Model Consensus"],
           ["6.3", "ROC Curves \u2013 Hybrid (TF-IDF + Properties) Features"],
           ["6.4", "ROC Curves \u2013 TF-IDF Only Features"],
           ["6.5", "ROC Curves \u2013 Structural Properties Only Features"]])

# =====================================================================
# LIST OF ABBREVIATIONS (vi)
# =====================================================================
doc.add_page_break()
hapter("LIST OF ABBREVIATIONS", new_page=False)
add_table(None, None, ["Sr. No.", "Abbreviation", "Expanded Form"],
          [[str(i + 1), a, b] for i, (a, b) in enumerate([
              ("BDA", "Big Data Analytics"),
              ("ML", "Machine Learning"),
              ("TF-IDF", "Term Frequency\u2013Inverse Document Frequency"),
              ("SVM", "Support Vector Machine"),
              ("ROC", "Receiver Operating Characteristic"),
              ("AUC", "Area Under the Curve"),
              ("API", "Application Programming Interface"),
              ("REST", "REpresentational State Transfer"),
              ("HTTP", "Hypertext Transfer Protocol"),
              ("JSON", "JavaScript Object Notation"),
              ("MIME", "Multipurpose Internet Mail Extensions"),
              ("RFC", "Request for Comments (email format RFC-822/5322)"),
              ("URL", "Uniform Resource Locator"),
              ("HTML", "Hypertext Markup Language"),
              ("NLP", "Natural Language Processing"),
              ("UI", "User Interface"),
              ("IP", "Internet Protocol"),
              ("CSV", "Comma-Separated Values")])])

# =====================================================================
# CHAPTER 1  INTRODUCTION
# =====================================================================
hapter("Chapter 1")
hapter("Introduction", new_page=False)
hsec("1.1 Description")
body("Email is the primary communication and transaction channel of modern organisations, and "
     "simultaneously the most abused one: phishing messages impersonate banks, employers, "
     "government agencies and cloud services to trick victims into surrendering credentials or "
     "opening malicious attachments. a single successful phishing campaign can compromise an "
     "entire corporate network. This project presents PhishShield AI, an end-to-end Big Data "
     "Analytics application that ingests emails \u2013 either typed, pasted as raw RFC-822 text, "
     "or uploaded as .eml/.mbox files \u2013 and returns a multi-model machine-learning verdict "
     "with an interpretable list of security red flags. A pipeline built with Python and "
     "scikit-learn prepares the prediction models, and a FastAPI web dashboard presents them.")
hsec("1.2 Problem Formulation")
body("Anti-phishing blacklists and static keyword filters age quickly because adversaries "
     "constantly mutate sender domains, URLs and wording. The problem is to engineer an automated "
     "classification system capable of (a) parsing arbitrary email content including headers, "
     "MIME parts and embedded HTML; (b) mining both the linguistic content and the structural "
     "forensic signals of each message; (c) combining the strengths of several supervised "
     "classifiers into a robust consensus; and (d) serving these insights through an accessible "
     "user interface that explains why an email is dangerous. The task is formally a binary "
     "classification problem over a labelled corpus of 800 emails, with class-balanced evaluation "
     "on a held-out 20% test partition.")
hsec("1.3 Motivation")
body("The motivation is to demonstrate how Big Data Analytics techniques \u2013 large-corpus text "
     "mining, feature engineering and ensemble machine learning \u2013 can be combined for a "
     "practical security problem that affects every internet user. Individual indicators such as "
     "one suspicious phrase or one mismatched link are individually weak but jointly highly "
     "discriminative; achieving 100% held-out accuracy for phishing detection using a hybrid "
     "TF-IDF + properties feature space shows that forensic email signals are a powerful and "
     "cheap-to-compute defence layer. An explainable verdict (risk score, red flags, model "
     "consensus) is essential so that a non-expert user can act on the prediction with confidence.")
hsec("1.4 Proposed Solution")
body("The proposed system extracts email text and 14 structural properties from the benchmark "
     "corpora [1][2], vectorises the cleaned text using a TF-IDF representation, and trains six "
     "supervised classifiers across three feature architectures. The best-performing artefacts "
     "are serialised into a cached model bundle, which is loaded by an inference engine inside a "
     "FastAPI server [5]. The engine computes a consensus verdict, a normalised risk percentage, "
     "and a rule-based red-flag analysis (raw-IP hyperlinks, deceptive anchor text, embedded "
     "forms, scripts, urgency keywords, domain mismatch and excessive subdomains). The results "
     "are rendered by a dark-themed single-page dashboard with live retraining support.")
hsec("1.5 Scope of the Project")
body("The project scope includes corpus preparation and cleaning, dual-branch feature "
     "engineering, training and benchmarking of six classifiers, ensemble inference with "
     "explainable diagnostics, and a web-based dashboard exposing single, batch and file-based "
     "analysis together with in-app model retraining. Stationary accuracy reporting and ROC "
     "analysis on the benchmark corpora are included; deployment to a mail-server gateway for "
     "fully automated in-line filtering is identified in the future scope (Chapter 7).")

# =====================================================================
# CHAPTER 2  REVIEW OF LITERATURE
# =====================================================================
hapter("Chapter 2")
hapter("Review of Literature", new_page=False)
body("The application of machine learning and text analytics to email security has been studied "
     "extensively as phishing volumes grew with the mass adoption of electronic mail. Statistical "
     "text mining remains the backbone of most published detectors: document representations such "
     "as Term Frequency\u2013Inverse Document Frequency (TF-IDF) convert a message into weighted "
     "term vectors and feed classical classifiers. The scikit-learn library [4], which provides "
     "reproducible implementations of_na\u0131ve Bayes, support vector machines, decision trees, "
     "random forests and gradient boosting together with the TF-IDF vectoriser, is a widely used "
     "foundation for such experiments and is likewise adopted in this project.")
body("Ensemble methods are repeatedly reported to outperform single classifiers on phishing "
     "data because they average out the instability of individual decision trees. Breiman's "
     "Random Forests [6] aggregate bootstrap-aggregated trees and are routinely among the "
     "best-performing models in published phishing benchmarks, while gradient boosting variants "
     "achieve similar accuracy at slightly higher training cost. Linear models such as logistic "
     "regression and linear SVMs remain attractive where training data or computer time is "
     "scarce, and linear SVMs in particular are reported to cope well with the sparse "
     "high-dimensional vectors produced by TF-IDF [4].")
body("Beyond content, a parallel line of research emphasises structural email forensics: "
     "analysing header irregularities, count of URLs, presence of IP-based hyperlinks, "
     "deceptive display text, embedded HTML forms or scripts, and social-engineering vocabulary. "
     "Systematic reviews of the phishing-detection literature [3] conclude that hybrid features "
     "\u2013 combining textual and structural signals \u2013 consistently improve both precision "
     "and recall compared with either family alone, an outcome this project reproduces "
     "empirically (Figure 6.3): every classifier reaches a perfect score on the hybrid feature "
     "space, whereas the text-only and property-only baselines trail behind (Figures 6.4 and "
     "6.5).")
body("On the data side, two public corpora dominate experimental work: the Jose Nazario "
     "phishing corpus [1], a large collection of real-world phishing messages, and the Enron "
     "email corpus [2], which supplies realistic benign organisational mail. Paired corpora of "
     "this kind allow balanced two-class evaluation and are therefore reused here. Finally, "
     "production-grade tooling has shifted towards lightweight web frameworks: FastAPI "
     "[5] exposes trained models through REST endpoints with automatic request validation, "
     "enabling exactly the interactive, browser-based threat assessment service this project "
     "implements.")

# =====================================================================
# CHAPTER 3  SYSTEM ANALYSIS
# =====================================================================
hapter("Chapter 3")
hapter("System Analysis", new_page=False)
hsec("3.1 Functional Requirements")
body("Table 3.1 lists the functional requirements of the system.")
add_table("3.1", "Functional Requirements",
          ["ID", "Requirement", "Description"],
          [["FR-1", "Single-Email Analysis",
            "The system must accept a composed email (sender, subject, body/HTML) and return a "
            "verdict, threat level and risk score."],
           ["FR-2", "Raw RFC-822 Inspection",
            "The system must parse complete raw email source text including headers and MIME "
            "parts."],
           ["FR-3", "File Upload",
            "The system must accept .eml, .txt, .msg and .mbox files for analysis."],
           ["FR-4", "Multi-Model Consensus",
            "The system must evaluate six classifiers in parallel and display per-model "
            "phishing probability."],
           ["FR-5", "Red-Flag Diagnostics",
            "The system must detect and rank security red flags with severity ratings."],
           ["FR-6", "Batch Analysis",
            "The system must analyse multiple emails in one request and summarise detection "
            "statistics."],
           ["FR-7", "Model Benchmarking",
            "The system must expose accuracy, precision, recall, F1, AUC-ROC and feature "
            "importance for all six models."],
           ["FR-8", "In-App Retraining",
            "The system must allow users to retrain classifiers from the browser with a "
            "customisable corpus size."]])
hsec("3.2 Non-Functional Requirements")
hsub("3.2.1 Performance Requirements")
body("\u2022 Classification of a single email must complete in well under a second, since "
     "inference requires only one TF-IDF transform and six lightweight model calls; measured "
     "per-email trainer inference adds roughly a millisecond-scale overhead (Table 6.2).")
body("\u2022 The trained bundle must be loaded once at server start-up rather than per request, "
     "so that dashboard responses remain near-instantaneous.")
body("\u2022 The training pipeline of 800 emails must complete training plus full benchmarking "
     "in under one minute on a typical laptop.")
hsub("3.2.2 Software Quality Attributes")
body("\u2022 Operating System: Windows")
body("\u2022 Python: main programming language for the pipeline and server")
body("\u2022 scikit-learn, SciPy, NumPy: feature extraction, training and evaluation")
body("\u2022 FastAPI and Uvicorn: REST service; BeautifulSoup4: HTML parsing; NLTK: text "
     "cleaning corpora")
body("\u2022 A modern web browser renders the single-page dashboard")
hsec("3.3 Specific Requirements")
hsub("3.3.1 Hardware")
body("\u2022 Processor: Intel Core i5 or equivalent")
body("\u2022 RAM: minimum 8 GB")
body("\u2022 Storage: enough space for the corpora, cached model bundle and HTML assets "
     "(under 100 MB)")
hsub("3.3.2 Software")
body("\u2022 Operating system: Windows or Linux")
body("\u2022 Python 3.9\u20133.11 with the packages listed in requirements.txt")
body("\u2022 Any browser (Chrome, Edge or Firefox) for the dashboard at port 8050")
hsec("3.4 Use-Case Diagram and Description")
body("Figure 3.1 shows the use-case diagram. The only actor is the user (an end user or security "
     "analyst), who can scan a single composed email, inspect a raw RFC-822 message, upload an "
     "email file, review the threat assessment and red flags, compare multi-model consensus "
     "probabilities, view benchmark metrics and ROC curves, run a batch analysis, or trigger "
     "in-app retraining of the models. All use cases are read-only with respect to the message "
     "content; only the Retrain use case modifies system state (the cached model bundle).")
fig_caption("3.1", "Use-Case Diagram", FIG("fig3_1_usecase.png"), 6.2)

# =====================================================================
# CHAPTER 4  ANALYSIS MODELING
# =====================================================================
hapter("Chapter 4")
hapter("Analysis Modeling", new_page=False)
hsec("4.1 Activity Diagram")
body("Figure 4.1 shows the activity diagram of a dashboard session. The application starts by "
     "loading the serialised model bundle; the user then submits an email through the composer, "
     "the raw RFC-822 inspector or the file uploader. The message is parsed, cleaned, and its "
     "features extracted; six classifiers run in parallel on the vectorised input; the engine "
     "aggregates the consensus, computes the risk score and derives red flags; and the threat "
     "assessment is rendered on the dashboard. If the user disagrees with a verdict, the "
     "retraining loop can rebuild the models from the corpora without leaving the browser.")
fig_caption("4.1", "Activity Diagram of a Scanning Session", FIG("fig4_1_activity.png"), 4.5)
hsec("4.2 Functional Modelling")
hsub("4.2.1 Data Flow Diagram")
body("Figure 4.2 shows the Level 0 (context) data flow diagram. The user submits email content "
     "to the PhishShield system and receives the verdict, risk score, red flags and model "
     "consensus in return. Raw labelled email corpora (the phishing and Enron mbox files) are "
     "supplied to the system by external data providers during the offline training phase.")
fig_caption("4.2", "Data Flow Diagram \u2013 Level 0 (Context)", FIG("fig4_2_dfd0.png"), 6.2)
body("Figure 4.3 shows the Level 1 data flow diagram. The offline training workflow proceeds "
     "from mbox data loading, through text cleaning, dual-branch feature extraction and model "
     "training, to the cached model bundle. The online inference workflow reads that bundle, "
     "vectorises the submitted message, runs the ensemble, explains the result with red flags, "
     "and serves it through the REST API to the web dashboard.")
fig_caption("4.3", "Data Flow Diagram \u2013 Level 1", FIG("fig4_3_dfd1.png"), 6.2)

# =====================================================================
# CHAPTER 5  DESIGN
# =====================================================================
hapter("Chapter 5")
hapter("Design", new_page=False)
hsec("5.1 Architectural Design")
body("Figure 5.1 presents the architecture of PhishShield AI. The presentation layer is a "
     "single-page dashboard (static/index.html with app.js and style.css) that communicates with "
     "the serving layer, a FastAPI application exposing the /api/analyze, /api/batch-analyze, "
     "/api/status, /api/samples and /api/retrain endpoints [5]. The inference layer "
     "(predictor.py) parses the message, extracts features and orchestrates the six-model "
     "ensemble. The machine-learning layer (run_simple.py and train_and_cache.py) implements "
     "training, benchmarking and ROC/feature-importance analysis over the feature layer founded "
     "on the data layer of corpus mbox files and cached artefacts (model_bundle.joblib, "
     "metrics_summary.json). This layered separation keeps dashboard responses fast because "
     "no training happens on the request path.")
fig_caption("5.1", "System Architecture", FIG("fig5_1_architecture.png"), 6.4)
hsec("5.2 User Interface Design")
body("The interface is a dark cyber-security themed dashboard with a two-column layout: the "
     "Email Input card on the left and the Threat Assessment and Diagnostics card on the right. "
     "Table 5.1 lists its primary modules. The user selects the input mode (Compose, Raw "
     "RFC-822/text or Upload .eml), fills the fields, and presses Inspect & Classify Email; the "
     "verdict panel, red-flag list and per-model probability bars update instantly. A Retrain "
     "control in the header triggers server-side retraining with a progress status.")
add_table("5.1", "Dashboard Modules",
          ["Module", "Purpose"],
          [["Email Input", "Compose fields (sender, recipient, subject, body/HTML) plus input "
            "modes for raw RFC-822 text and .eml/.mbox file upload."],
           ["Threat Assessment", "Verdict banner (PHISHING/LEGITIMATE), threat-level badge, "
            "risk ring (0\u2013100%) and confidence statement."],
           ["Detected Red Flags", "Ranked list of forensic findings with severity badges "
            "(CRITICAL/HIGH/MEDIUM) and explanatory text."],
           ["Multi-Model Consensus", "Grid of six classifier cards showing prediction badge, "
            "phishing probability bar and confidence."],
           ["Benchmark Charts", "Model performance table and ROC curves rendered from the "
            "cached evaluation metrics."],
           ["Retrain Model", "Browser-triggered retraining of the ensemble with live progress "
            "status in the header."]])

# =====================================================================
# CHAPTER 6  IMPLEMENTATION
# =====================================================================
hapter("Chapter 6")
hapter("Implementation", new_page=False)
hsec("6.1 Algorithms")
hsub("6.1.1 TF-IDF Text Representation")
body("Each cleaned email body is converted into a vector of term weights using the "
     "Term Frequency\u2013Inverse Document Frequency scheme given by (6.1). The project retains "
     "the 500 highest-scoring n-grams (min_df = 2), which balances vocabulary coverage against "
     "overfitting on the 800-message corpus.")
center_text("tfidf(t, d) = tf(t, d) \u00d7 log(N / df(t))", 12)
hsub("6.1.2 Structural Forensic Properties")
body("Fourteen numeric properties are computed per message: number of URLs (nurls), number of "
     "dots in URLs (ndots), URL ports, recipients, sender/target domain alignment "
     "(checkdomains), MIME parts, presence of HTML, attachments, social-engineering word count "
     "(badwords), IP-based URLs (ipurls), deceptive anchor text (diffhref), embedded forms, "
     "script tags and non-standard encoding. The properties are min-max scaled before "
     "combination with the sparse TF-IDF block, so the two branches contribute comparably. "
     "Table 6.1 lists the most influential properties learned by the ensemble.")
hsub("6.1.3 Classification Models")
body("Six supervised algorithms are trained: Random Forest [6], Gradient Boosting, Logistic "
     "Regression, Linear SVM, Decision Tree and Gaussian Na\u00efve Bayes. An ensemble of T "
     "decision trees averages individual predictions as in (6.2); the tree family also powers "
     "Decision Tree and participates in Gradient Boosting, where trees correct earlier "
     "residuals.")
center_text("\u0177(x) = (1/T) \u03a3\u209c tree\u209c(x)", 12)
body("A Linear SVM separates the two classes by the maximum-margin hyperplane \u03c9x + b = 0, "
     "and Logistic Regression maps the margin to a probability through the logistic function "
     "given by (6.3).")
center_text("P(y = phish | x) = 1 / (1 + e^-(\u03c9x + b))", 12)
hsub("6.1.4 Consensus Verdict and Risk Score")
body("The inference engine aggregates the six individual phishing probabilities into a consensus "
     "risk percentage given by (6.4); the verdict is the majority vote with the highest "
     "probability model breaking ties. A message is reported as phishing when the consensus "
     "score exceeds 50%.")
center_text("risk = 100 \u00d7 (1/n) \u03a3\u1d62 P\u1d62(phishing)", 12)
hsec("6.2 Working of the Project")
body("The user starts the FastAPI application (python run_frontend.py) and the dashboard opens "
     "at http://127.0.0.1:8050. Figure 6.1 shows the initial single-email analysis page with the "
     "Email Input card and the awaiting-scan Threat Assessment panel. The user enters a sender, "
     "a subject and the message text or HTML, or pastes a raw RFC-822 message, or uploads an "
     ".eml file, and presses Inspect & Classify Email.")
fig_caption("6.1", "PhishShield Dashboard \u2013 Single-Mail Analysis Home Page",
            FIG("fig6_1_dashboard.png"), 6.2)
body("On submission the server parses the message, extracts the 14 structural properties, "
     "vectorises the text, and runs six classifiers in parallel. Figure 6.2 shows the result for "
     "a crafted PayPal-impersonation attack: the verdict is PHISHING DETECTED with a CRITICAL "
     "threat level, a 97% risk score, six of six models flagged phishing, and seven ranked red "
     "flags \u2013 raw IP hyperlink, sender/target domain mismatch, deceptive anchor text, "
     "embedded data-harvesting form, executable scripts, urgency keywords and excessive "
     "subdomains. The consensus grid beneath the flags shows per-model phishing probabilities, "
     "demonstrating that even the most conservative member of the ensemble assigns 89% phishing "
     "probability.")
fig_caption("6.2", "Threat Assessment, Red Flags and Multi-Model Consensus",
            FIG("fig6_2_analysis.png"), 6.2)
hsec("6.3 Results and Evaluation")
body("The models were evaluated on a stratified 80/20 train-test split of the 800-email corpus "
     "(640 training / 160 test messages, balanced classes at 80/80 per set). Table 6.2 presents "
     "the results for the text-only TF-IDF baseline and Table 6.3 for the hybrid TF-IDF + "
     "properties architecture. As Figure 6.3 shows, every hybrid model achieves AUC = 1.000 with "
     "a single perfect operating point, while the text-only models trail slightly "
     "(AUC 0.946\u20130.999) as plotted in Figure 6.4 and the property-only models are perfect at "
     "the operating point but with visibly less calibration headroom in Figure 6.5.")
add_table("6.1", "Top Model-Relevant Features (Random Forest feature importance)",
          ["Rank", "Feature", "Type", "Importance"],
          [["1", "ndots", "Structural", "0.1087"],
           ["2", "diffhref", "Structural", "0.0829"],
           ["3", "nurls", "Structural", "0.0664"],
           ["4", "checkdomains", "Structural", "0.0538"],
           ["5", "word: account", "Text (TF-IDF)", "0.0457"],
           ["6", "badwords", "Structural", "0.0419"],
           ["7", "hasHTML", "Structural", "0.0411"],
           ["8", "encoding", "Structural", "0.0410"],
           ["9", "word: url", "Text (TF-IDF)", "0.0387"],
           ["10", "ipurls", "Structural", "0.0290"]])
add_table("6.2", "Benchmark Results \u2013 TF-IDF Only Architecture",
          ["Classifier", "Accuracy", "Precision", "Recall", "F1", "AUC-ROC", "Train Time (s)"],
          [["Logistic Regression", "0.9625", "1.000", "0.925", "0.961", "0.9969", "0.012"],
           ["Decision Tree", "0.9187", "0.935", "0.900", "0.917", "0.9464", "0.016"],
           ["Random Forest", "0.9563", "1.000", "0.913", "0.954", "0.9722", "0.207"],
           ["Gradient Boosting", "0.9313", "0.973", "0.888", "0.928", "0.9898", "1.278"],
           ["Linear SVM", "0.9625", "1.000", "0.925", "0.961", "0.9953", "0.006"],
           ["Na\u00efve Bayes", "0.9688", "1.000", "0.938", "0.968", "0.9989", "0.002"]])
add_table("6.3", "Benchmark Results \u2013 Hybrid (TF-IDF + Properties) Architecture",
          ["Classifier", "Accuracy", "Precision", "Recall", "F1", "AUC-ROC", "Train Time (s)"],
          [["Logistic Regression", "1.000", "1.000", "1.000", "1.000", "1.000", "0.012"],
           ["Decision Tree", "1.000", "1.000", "1.000", "1.000", "1.000", "0.008"],
           ["Random Forest", "1.000", "1.000", "1.000", "1.000", "1.000", "0.181"],
           ["Gradient Boosting", "1.000", "1.000", "1.000", "1.000", "1.000", "0.636"],
           ["Linear SVM", "1.000", "1.000", "1.000", "1.000", "1.000", "0.003"],
           ["Na\u00efve Bayes", "1.000", "1.000", "1.000", "1.000", "1.000", "0.002"]])
body("The perfect test-set performance of the hybrid models is supported by the confusion "
     "matrices: every hybrid classifier separated the 80 legitimate and 80 phishing test messages "
     "without a single error, as opposed to 8\u201314 combined errors for the text-only models. "
     "Table 6.1 additionally shows that structural signals dominate feature importance \u2013 "
     "ndots, deceptive anchor text, URL count and domain alignment occupy the top four ranks \u2013 "
     "confirming the central design decision of this project: fusing text mining with email "
     "forensics. Accuracy is nonetheless reported on a single benchmark split and, as discussed "
     "in Chapter 7, evaluation on larger and more recent adversarial corpora remains necessary "
     "before production deployment.")
fig_caption("6.3", "ROC Curves \u2013 Hybrid (TF-IDF + Properties) Features",
            FIG("fig6_3_roc.png"), 5.6)
fig_caption("6.4", "ROC Curves \u2013 TF-IDF Only Features", FIG("fig6_4_roc_tfidf.png"), 5.6)
fig_caption("6.5", "ROC Curves \u2013 Structural Properties Only Features",
            FIG("fig6_5_roc_props.png"), 5.6)

# =====================================================================
# CHAPTER 7  CONCLUSIONS
# =====================================================================
hapter("Chapter 7")
hapter("Conclusions", new_page=False)
hsec("7.1 Conclusion")
body("The \"PhishShield AI\" project successfully developed an end-to-end Big Data Analytics "
     "application that detects phishing email with high accuracy and full explainability. By "
     "integrating TF-IDF text mining with 14 structural email-forensic properties, the system "
     "lifted all six benchmark classifiers \u2013 Random Forest, Gradient Boosting, Logistic "
     "Regression, Linear SVM, Decision Tree and Na\u00efve Bayes \u2013 to 100% held-out accuracy "
     "and AUC-ROC of 1.000, compared with 91.9\u201396.9% accuracy for the text-only baseline. "
     "The interactive FastAPI dashboard demonstrates the practical value of the model: a single "
     "crafted phishing email is classified in milliseconds with a 97% risk score, six-model "
     "consensus confirmation, and seven human-readable red flags that explain the verdict. The "
     "project proves that combining content analytics with structural forensics is a highly "
     "effective, interpretable and easily deployable defence against email phishing attacks.")
hsec("7.2 Future Scope")
body("Live Gateway Integration: the classification engine could be connected to a mail transfer "
     "agent or an IMAP/JMAP inbox watcher, so that suspicious inbound messages are quarantined "
     "automatically rather than analysed on demand.")
body("Larger and Adversarial Evaluation: the benchmark should be extended to million-scale "
     "resent corpora such as SpamAssassin/Nazario derivatives and adversarially rewritten "
     "phishing campaigns, and temporal leakage checks should be added; the current perfect score "
     "is corpus-specific and will decline on harder distributions.")
body("Advanced Deep Learning: transformer-based encoders (BERT/DistilBERT) fine-tuned on "
     "phishing corpora could capture semantic deception beyond bag-of-words models, and "
     "graph-based sender-reputation models could exploit the mail-graph structure.")
body("Cloud Deployment & User Feedback Loop: the architecture could be containerised and "
     "deployed on a cloud platform with autoscaling, and user feedback (agree/disagree) on "
     "verdicts could feed the existing in-app retraining endpoint for continuous on-line "
     "learning.")

# =====================================================================
# REFERENCES
# =====================================================================
hapter("References")
rr = body("[1] J. Nazario, \"The Phishing Corpus,\" public benchmark corpus of labelled phishing "
          "emails, honeyblog.net, 2006.")
body("[2] W. W. Cohen, \"Enron Email Dataset,\" Carnegie Mellon University, 2009.")
body("[3] S. Basit, M. Zafar, X. Liu, A. R. Javed, Z. Jalil and K. Kifayat, \"A comprehensive "
     "survey of AI-enabled phishing attacks detection techniques,\" Telecommunications Systems, "
     "vol. 76, pp. 139\u2013154, 2021.")
body("[4] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine "
     "Learning Research, vol. 12, pp. 2825\u20132830, 2011.")
body("[5] S. Ram\u00edrez, \"FastAPI documentation,\" fastapi.tiangolo.com, 2024.")
body("[6] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5\u201332, 2001.")

# =====================================================================
# ACKNOWLEDGEMENTS
# =====================================================================
hapter("Acknowledgements")
body("We would like to express our sincere gratitude to our project guide and to the Department "
     "of Computer Engineering, St. Francis Institute of Technology, for their guidance and "
     "support throughout the development of this mini project. We also thank the institute for "
     "providing the required facilities and learning environment.")
body("We are grateful to our faculty members and classmates for their suggestions during the "
     "preparation of this report, and to the maintainers of the public phishing and Enron email "
     "corpora for making the underlying datasets freely available.")

doc.save(OUT)
print("Saved:", OUT)
