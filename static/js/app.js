/**
 * PhishShield AI — Frontend Application Logic
 * Implements real-time analysis, interactive charts, and model benchmarks.
 */

// Global Application State
const AppState = {
  samples: [],
  metrics: null,
  activeFeatureSet: "TF-IDF + Properties",
  modelsComparisonChart: null,
  rocChart: null,
  featureImportanceChart: null,
  retrainPollInterval: null,
  batchResults: []
};

// Feature Definitions Dictionary
const FEATURE_DEFINITIONS = {
  nurls: {
    name: "Total URLs",
    type: "Quantity",
    desc: "Count of all hyperlinks embedded anywhere in email body, headers, or HTML tags.",
    impact: "High volume of outbound links increases probability of link cloaking or referral redirection chains."
  },
  ndots: {
    name: "Max Dots in URL",
    type: "Structural",
    desc: "The highest number of dot characters contained within any single extracted URL.",
    impact: "Subdomain nesting (e.g. login.bank.com.attacker.org) is a signature phishing cloaking technique."
  },
  nports: {
    name: "Port Numbers in URL",
    type: "Network",
    desc: "Count of hyperlinks explicitly specifying non-standard server ports (e.g., :8080, :4443).",
    impact: "Phishing kits often host rogue listener daemons on non-standard HTTP/HTTPS ports."
  },
  nrecs: {
    name: "Recipient Count",
    type: "Addressing",
    desc: "Total count of unique email addresses listed in To, Cc, and Bcc distribution fields.",
    impact: "Mass spraying attacks often target numerous recipients simultaneously or suppress visibility."
  },
  checkdomains: {
    name: "Domain Alignment",
    type: "Integrity",
    desc: "Binary check (1 if all hyperlinks match the sender's top-level domain; 0 if any link deviates).",
    impact: "A mismatch (0) indicates the email claims to be from Company A while directing users to Company B."
  },
  nparts: {
    name: "MIME Parts",
    type: "Structural",
    desc: "Number of MIME payload segments in the multipart email tree.",
    impact: "Multipart messages allow attackers to obfuscate payloads between text/plain and text/html."
  },
  hasHTML: {
    name: "HTML Payload",
    type: "Format",
    desc: "Binary indicator of whether rendered HTML content is included in the email.",
    impact: "HTML enables font spoofing, hidden text, CSS deception, and clickable spoofed hyperlinks."
  },
  attachments: {
    name: "Attachment Count",
    type: "Payload",
    desc: "Total number of file attachments encoded within the email.",
    impact: "Malware droppers, malicious PDFs, and disguised executables arrive via attachment payloads."
  },
  badwords: {
    name: "Urgency Keywords",
    type: "Social Engineering",
    desc: "Frequency of trigger words: link, click, confirm, user, customer, client, suspend, restrict, verify, protect.",
    impact: "Psychological urgency tactics exploit fear and panic to rush victims into compliance."
  },
  ipurls: {
    name: "IP-Based URLs",
    type: "Malicious Indicator",
    desc: "Number of URLs using direct numeric IP addresses instead of registered DNS domain names.",
    impact: "Nearly 100% of consumer-facing legitimate emails use domains. IP links strongly signal hostile infrastructure."
  },
  diffhref: {
    name: "Anchor Discrepancies",
    type: "Visual Deception",
    desc: "Number of anchor tags where the visible display text differs from the underlying href URL target.",
    impact: "Classic phishing decoy: displaying 'https://paypal.com' while routing to 'http://phishing-site.ru'."
  },
  forms: {
    name: "Embedded Forms",
    type: "Harvesting",
    desc: "Number of HTML <form> input containers embedded directly in the email content.",
    impact: "Used by credential harvesters to steal passwords without requiring the victim to navigate away."
  },
  scripts: {
    name: "Executable Scripts",
    type: "Execution",
    desc: "Number of <script> JavaScript tags embedded in the message.",
    impact: "Active scripts inside emails present extreme risk for cross-site scripting and automated exploits."
  },
  encoding: {
    name: "Transfer Encoding",
    type: "Encoding",
    desc: "MIME Content-Transfer-Encoding mechanism (base64, quoted-printable, 7bit, 8bit, none).",
    impact: "Unusual encoding layers are frequently leveraged to bypass perimeter email security gateways."
  }
};

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  initNavTabs();
  initInputModes();
  initEventListeners();
  loadSystemStatus();
  loadSamples();
});

// Navigation Tabs
function initNavTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");

      const targetTab = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      const targetPane = document.getElementById(`pane-${targetTab}`);
      if (targetPane) targetPane.classList.add("active");

      // Trigger resize and re-render for Chart.js canvases when switching tabs
      if (targetTab === "benchmarks") {
        if (!AppState.metrics) {
          loadMetricsAndBenchmarks();
        } else {
          setTimeout(() => {
            updateBenchmarkViews();
          }, 60);
        }
      } else if (targetTab === "features") {
        if (!AppState.metrics) {
          loadMetricsAndBenchmarks();
        } else {
          setTimeout(() => {
            if (AppState.metrics && AppState.metrics.feature_importances) {
              renderFeatureImportanceChart(AppState.metrics.feature_importances);
            }
          }, 60);
        }
      }
    });
  });
}

// Input Mode Toggles (Composer, Raw, Upload)
function initInputModes() {
  const modeBtns = document.querySelectorAll(".mode-btn");
  modeBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      modeBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const mode = btn.getAttribute("data-mode");
      document.getElementById("section-composer").classList.toggle("hidden", mode !== "composer");
      document.getElementById("section-raw").classList.toggle("hidden", mode !== "raw");
      document.getElementById("section-upload").classList.toggle("hidden", mode !== "upload");
    });
  });

  // Char counters
  const bodyInput = document.getElementById("inp-body");
  const rawInput = document.getElementById("inp-raw");
  if (bodyInput) {
    bodyInput.addEventListener("input", () => {
      document.getElementById("body-char-count").innerText = `${bodyInput.value.length} characters`;
    });
  }
  if (rawInput) {
    rawInput.addEventListener("input", () => {
      document.getElementById("raw-char-count").innerText = `${rawInput.value.length} characters`;
    });
  }
}

// Event Listeners
function initEventListeners() {
  // Analyze CTA
  document.getElementById("btn-analyze").addEventListener("click", handleAnalyzeClick);

  // Clear input
  document.getElementById("btn-clear-input").addEventListener("click", () => {
    document.getElementById("inp-sender").value = "";
    document.getElementById("inp-recipient").value = "";
    document.getElementById("inp-subject").value = "";
    document.getElementById("inp-body").value = "";
    document.getElementById("inp-raw").value = "";
    document.getElementById("body-char-count").innerText = "0 characters";
    document.getElementById("raw-char-count").innerText = "0 characters";
    document.getElementById("file-loaded-info").classList.add("hidden");
    showToast("Input fields cleared", "info");
  });

  // Paste clipboard
  document.getElementById("btn-paste-clipboard").addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      const activeMode = document.querySelector(".mode-btn.active").getAttribute("data-mode");
      if (activeMode === "composer") {
        document.getElementById("inp-body").value = text;
        document.getElementById("body-char-count").innerText = `${text.length} characters`;
      } else {
        document.getElementById("inp-raw").value = text;
        document.getElementById("raw-char-count").innerText = `${text.length} characters`;
      }
      showToast("Content pasted from clipboard", "info");
    } catch (err) {
      showToast("Clipboard access denied or unavailable", "error");
    }
  });

  // Drag & drop
  const dropzone = document.getElementById("email-dropzone");
  const fileInput = document.getElementById("file-input");

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });


  // Retrain modal controls
  const retrainModal = document.getElementById("retrain-modal");
  document.getElementById("btn-open-retrain").addEventListener("click", () => {
    retrainModal.classList.remove("hidden");
  });
  document.getElementById("btn-close-modal").addEventListener("click", () => {
    retrainModal.classList.add("hidden");
  });
  document.getElementById("btn-cancel-retrain").addEventListener("click", () => {
    retrainModal.classList.add("hidden");
  });

  const rangeSlider = document.getElementById("retrain-sample-size");
  const rangeValText = document.getElementById("range-val-text");
  rangeSlider.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    rangeValText.innerText = `${val} (${val * 2} total)`;
  });

  document.getElementById("btn-start-retrain").addEventListener("click", handleStartRetrain);
}

// Handle File Input (.eml, .txt)
function handleFileSelected(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    document.getElementById("file-loaded-name").innerText = file.name;
    document.getElementById("file-loaded-info").classList.remove("hidden");
    // Switch to raw mode and populate
    document.getElementById("mode-raw").click();
    document.getElementById("inp-raw").value = content;
    document.getElementById("raw-char-count").innerText = `${content.length} characters`;
    showToast(`Loaded ${file.name} (${Math.round(file.size / 1024)} KB)`, "success");
  };
  reader.readAsText(file);
}

// ==========================================================================
// API CALLS & DATA RETRIEVAL
// ==========================================================================

async function loadSystemStatus() {
  const statusChip = document.querySelector(".system-status-chip");
  const statusText = document.getElementById("status-chip-text");
  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error(`Status request failed (${res.status})`);
    const data = await res.json();
    statusText.innerText = `${data.models_loaded || 6} Models Active`;
    statusChip.classList.remove("is-loading", "is-offline");
    statusChip.classList.add("is-online");
  } catch (e) {
    console.error("Failed to load status:", e);
    statusText.innerText = "Unavailable";
    statusChip.classList.remove("is-loading", "is-online");
    statusChip.classList.add("is-offline");
  }
}

async function loadSamples() {
  try {
    const res = await fetch("/api/samples");
    if (!res.ok) return;
    const data = await res.json();
    AppState.samples = data.samples || [];
    renderSamplePills(AppState.samples);
  } catch (e) {
    console.error("Failed to load samples:", e);
  }
}

function renderSamplePills(samples) {
  const container = document.getElementById("samples-pills-container");
  if (!container) return;
  container.innerHTML = "";
  samples.forEach((sample, idx) => {
    const pill = document.createElement("button");
    const isPhish = sample.category === "Phishing";
    pill.id = `sample-btn-${sample.id || idx}`;
    pill.className = `sample-pill ${isPhish ? 'phish' : 'legit'}`;
    pill.innerText = sample.label;
    pill.title = `Click to load: ${sample.subject}`;
    pill.addEventListener("click", (e) => {
      e.preventDefault();
      loadSampleIntoComposer(sample);
    });
    container.appendChild(pill);
  });
}

function loadSampleIntoComposer(sample, autoAnalyze = true) {
  // Switch to Composer mode
  const compBtn = document.getElementById("mode-composer");
  if (compBtn) compBtn.click();
  
  document.getElementById("inp-sender").value = sample.sender || "";
  document.getElementById("inp-recipient").value = sample.recipient || "";
  document.getElementById("inp-subject").value = sample.subject || "";
  document.getElementById("inp-body").value = sample.body || "";
  document.getElementById("body-char-count").innerText = `${(sample.body || '').length} characters`;

  showToast(`Loaded: ${sample.subject.slice(0, 32)}...`, "info");

  if (autoAnalyze) {
    handleAnalyzeClick();
  }
}

async function loadMetricsAndBenchmarks() {
  try {
    const res = await fetch("/api/metrics");
    if (!res.ok) return;
    const data = await res.json();
    AppState.metrics = data;

    updateBenchmarkViews();
    renderFeatureImportanceChart(data.feature_importances);
  } catch (e) {
    console.error("Failed to load metrics:", e);
  }
}

// ==========================================================================
// ANALYSIS LOGIC & RENDERING
// ==========================================================================

async function handleAnalyzeClick() {
  const activeMode = document.querySelector(".mode-btn.active").getAttribute("data-mode");
  let payload = {};

  if (activeMode === "composer") {
    const body = document.getElementById("inp-body").value.trim();
    if (!body) {
      showToast("Please enter an email body or select a sample.", "error");
      return;
    }
    payload = {
      text: body,
      sender: document.getElementById("inp-sender").value.trim(),
      recipient: document.getElementById("inp-recipient").value.trim(),
      subject: document.getElementById("inp-subject").value.trim()
    };
  } else {
    const raw = document.getElementById("inp-raw").value.trim();
    if (!raw) {
      showToast("Please enter or paste raw email content.", "error");
      return;
    }
    payload = { text: raw };
  }

  // Loading state
  const btn = document.getElementById("btn-analyze");
  const spinner = document.getElementById("analyze-spinner");
  const icon = document.getElementById("analyze-icon");
  const btnText = document.getElementById("analyze-btn-text");

  btn.disabled = true;
  document.querySelector(".input-panel").classList.add("is-scanning");
  spinner.classList.remove("hidden");
  icon.classList.add("hidden");
  btnText.innerText = "Analyzing Features...";

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Inference failed");
    }

    const result = await res.json();
    renderAnalysisResults(result);
    showToast(`Analysis complete: ${result.verdict} (${result.risk_score}% Risk)`, result.is_phishing ? "error" : "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    document.querySelector(".input-panel").classList.remove("is-scanning");
    spinner.classList.add("hidden");
    icon.classList.remove("hidden");
    btnText.innerText = "Inspect & Classify Email";
  }
}

function renderAnalysisResults(res) {
  // Hide empty state, show results
  document.getElementById("analysis-empty-state").classList.add("hidden");
  document.getElementById("results-content").classList.remove("hidden");

  // Timestamp
  document.getElementById("analysis-timestamp").innerText = `Last scan: ${new Date().toLocaleTimeString()}`;

  // 1. Verdict Banner
  const banner = document.getElementById("verdict-banner");
  const isPhish = res.is_phishing;
  banner.className = `verdict-banner ${isPhish ? 'is-phish' : 'is-legit'}`;

  document.getElementById("threat-level-badge").innerText = res.threat_level;
  document.getElementById("consensus-tag").innerText = `${res.phishing_votes} of ${res.total_models} Models Flagged Phishing`;
  document.getElementById("verdict-headline").innerText = isPhish ? "PHISHING DETECTED" : "LEGITIMATE EMAIL";

  if (isPhish) {
    document.getElementById("verdict-summary").innerText =
      "High probability of deceptive intent. Structural heuristics, domain discrepancies, and social engineering language indicate a security risk.";
  } else {
    document.getElementById("verdict-summary").innerText =
      "Email passes safety thresholds. Feature parameters are consistent with authentic workplace correspondence and normal MIME structure.";
  }

  // Circular Risk Gauge
  const ringBar = document.getElementById("progress-ring-bar");
  const riskScore = res.risk_score;
  const radius = 46;
  const circumference = 2 * Math.PI * radius; // ~289
  const offset = circumference - (riskScore / 100) * circumference;

  ringBar.style.stroke = res.badge_color;
  ringBar.style.strokeDasharray = `${circumference} ${circumference}`;
  ringBar.style.strokeDashoffset = circumference;
  const riskScoreValue = document.getElementById("risk-score-value");
  riskScoreValue.innerText = "0%";
  requestAnimationFrame(() => {
    ringBar.style.strokeDashoffset = offset;
  });
  const animationStart = performance.now();
  const animateRiskScore = (now) => {
    const progress = Math.min((now - animationStart) / 850, 1);
    const easedProgress = 1 - Math.pow(1 - progress, 3);
    riskScoreValue.innerText = `${Math.round(riskScore * easedProgress)}%`;
    if (progress < 1) requestAnimationFrame(animateRiskScore);
  };
  requestAnimationFrame(animateRiskScore);

  // 2. Red Flags Section
  const flagsList = document.getElementById("flags-list");
  const flagCountBadge = document.getElementById("flag-count-badge");
  flagsList.innerHTML = "";

  if (res.red_flags && res.red_flags.length > 0) {
    document.getElementById("red-flags-section").classList.remove("hidden");
    flagCountBadge.innerText = `${res.red_flags.length} Flag${res.red_flags.length > 1 ? 's' : ''}`;
    res.red_flags.forEach(flag => {
      const item = document.createElement("details");
      item.className = "flag-item";
      item.open = true;
      item.innerHTML = `
        <summary class="flag-header">
          <span class="flag-title">${flag.title}</span>
          <span class="flag-sev ${flag.severity}">${flag.severity}</span>
        </summary>
        <p class="flag-detail">${flag.detail}</p>
      `;
      flagsList.appendChild(item);
    });
  } else {
    flagCountBadge.innerText = "0 Flags";
    flagsList.innerHTML = `
      <div class="flag-item" style="border-left-color: var(--emerald); background: rgba(16, 185, 129, 0.08);">
        <div class="flag-header">
          <span class="flag-title" style="color: var(--emerald);"><i class="fa-solid fa-circle-check"></i> Clean Profile</span>
          <span class="flag-sev" style="background: var(--emerald);">SAFE</span>
        </div>
        <p class="flag-detail">No anomalous hyperlinks, IP addresses, embedded forms, or urgency patterns detected in this email.</p>
      </div>
    `;
  }

  // 3. Multi-Classifier Consensus Row
  const modelsRow = document.getElementById("models-cards-row");
  modelsRow.innerHTML = "";
  if (res.models_breakdown) {
    res.models_breakdown.forEach(m => {
      const card = document.createElement("div");
      card.className = "model-card";
      const isMPhish = m.is_phishing;
      const probPct = Math.round(m.phishing_prob * 100);
      card.innerHTML = `
        <div class="model-card-top">
          <span class="model-name">${m.classifier}</span>
          <span class="model-verdict-chip ${isMPhish ? 'phish' : 'legit'}">${m.prediction}</span>
        </div>
        <div class="model-bar-wrap">
          <div class="model-bar-fill" style="width: ${probPct}%; background: ${isMPhish ? 'var(--danger)' : 'var(--emerald)'};"></div>
        </div>
        <div class="model-confidence-text">
          <span>Phish Prob: ${probPct}%</span>
          <span>Conf: ${Math.round(m.confidence * 100)}%</span>
        </div>
      `;
      modelsRow.appendChild(card);
    });
  }

}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

// ==========================================================================
// BENCHMARKS & EVALUATION VIEWS
// ==========================================================================

function updateBenchmarkViews() {
  if (!document.getElementById("pane-benchmarks")) return;
  if (!AppState.metrics || !AppState.metrics.benchmarks) return;

  const activeSet = AppState.activeFeatureSet;
  const filtered = AppState.metrics.benchmarks.filter(b => b.features === activeSet);

  // Find best
  const sorted = [...filtered].sort((a, b) => b.f1 - a.f1);
  if (sorted.length > 0) {
    const best = sorted[0];
    document.getElementById("kpi-best-clf").innerText = best.classifier;
    document.getElementById("kpi-best-f1").innerText = `F1: ${(best.f1 * 100).toFixed(1)}% / Acc: ${(best.accuracy * 100).toFixed(1)}%`;

    const maxAcc = Math.max(...filtered.map(x => x.accuracy));
    const maxAuc = Math.max(...filtered.map(x => x.auc_roc));
    document.getElementById("kpi-max-acc").innerText = `${(maxAcc * 100).toFixed(1)}%`;
    document.getElementById("kpi-max-auc").innerText = maxAuc.toFixed(3);
  }

  // Update Table
  renderBenchmarksTable(filtered);

  // Update Comparison Chart
  renderComparisonChart(filtered);

  // Update ROC Chart
  renderRocChart(activeSet);

  // Update static ROC plot path
  updateStaticRocImage();
}

function renderBenchmarksTable(benchmarks) {
  const tbody = document.getElementById("tbody-benchmarks");
  tbody.innerHTML = "";

  benchmarks.forEach(b => {
    const tr = document.createElement("tr");

    // Confusion Matrix Mini-Grid
    const cm = b.confusion_matrix || [[0, 0], [0, 0]];
    const cmHtml = `
      <div class="cm-mini" title="TN: ${cm[0][0]}, FP: ${cm[0][1]} / FN: ${cm[1][0]}, TP: ${cm[1][1]}">
        <span class="cm-cell cm-tn">${cm[0][0]}</span>
        <span class="cm-cell cm-fp">${cm[0][1]}</span>
        <span class="cm-cell cm-fn">${cm[1][0]}</span>
        <span class="cm-cell cm-tp">${cm[1][1]}</span>
      </div>
    `;

    tr.innerHTML = `
      <td>
        <div class="clf-name-cell">
          <i class="fa-solid fa-cube text-cyan"></i>
          <span>${b.classifier}</span>
        </div>
      </td>
      <td><span class="badge" style="background: rgba(255,255,255,0.05);">${b.features}</span></td>
      <td><span class="metric-pill ${b.accuracy >= 0.95 ? 'pill-high' : 'pill-mid'}">${(b.accuracy * 100).toFixed(1)}%</span></td>
      <td><span class="metric-pill ${(b.precision || 0) >= 0.95 ? 'pill-high' : 'pill-mid'}">${((b.precision || 0) * 100).toFixed(1)}%</span></td>
      <td><span class="metric-pill ${(b.recall || 0) >= 0.95 ? 'pill-high' : 'pill-mid'}">${((b.recall || 0) * 100).toFixed(1)}%</span></td>
      <td><span class="metric-pill ${b.f1 >= 0.95 ? 'pill-high' : 'pill-mid'}">${(b.f1 * 100).toFixed(1)}%</span></td>
      <td><span class="metric-pill ${b.auc_roc >= 0.98 ? 'pill-high' : 'pill-mid'}">${(b.auc_roc || 0).toFixed(3)}</span></td>
      <td class="code-font text-dim">${b.time_sec}s</td>
      <td>${cmHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderComparisonChart(benchmarks) {
  const ctx = document.getElementById("chart-models-comparison").getContext("2d");

  const labels = benchmarks.map(b => b.classifier);
  const accData = benchmarks.map(b => +(b.accuracy * 100).toFixed(1));
  const f1Data = benchmarks.map(b => +(b.f1 * 100).toFixed(1));
  const aucData = benchmarks.map(b => +((b.auc_roc || 0) * 100).toFixed(1));

  if (AppState.modelsComparisonChart) {
    AppState.modelsComparisonChart.destroy();
  }

  AppState.modelsComparisonChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Accuracy %",
          data: accData,
          backgroundColor: "rgba(6, 182, 212, 0.7)",
          borderColor: "#06b6d4",
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: "F1-Score %",
          data: f1Data,
          backgroundColor: "rgba(139, 92, 246, 0.7)",
          borderColor: "#8b5cf6",
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: "AUC-ROC (x100)",
          data: aucData,
          backgroundColor: "rgba(16, 185, 129, 0.7)",
          borderColor: "#10b981",
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { family: "Inter", size: 12 } }
        },
        tooltip: {
          backgroundColor: "rgba(15, 23, 42, 0.95)",
          titleColor: "#fff",
          bodyColor: "#94a3b8",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1
        }
      },
      scales: {
        x: {
          ticks: { color: "#94a3b8", font: { family: "Inter", size: 11 } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          min: 80,
          max: 100,
          ticks: { color: "#94a3b8", font: { family: "JetBrains Mono", size: 11 } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        }
      }
    }
  });
}

function renderRocChart(featureSet) {
  const ctx = document.getElementById("chart-roc").getContext("2d");
  const rocData = AppState.metrics ? AppState.metrics.roc_data[featureSet] : null;

  if (AppState.rocChart) {
    AppState.rocChart.destroy();
  }

  if (!rocData) return;

  const colorPalette = [
    "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#3b82f6"
  ];

  const datasets = [];
  let colorIdx = 0;

  for (const [clfName, item] of Object.entries(rocData)) {
    const points = item.fpr.map((fprVal, i) => ({
      x: fprVal,
      y: item.tpr[i]
    }));

    datasets.push({
      label: `${clfName} (AUC=${item.auc.toFixed(3)})`,
      data: points,
      borderColor: colorPalette[colorIdx % colorPalette.length],
      backgroundColor: "transparent",
      borderWidth: 2,
      tension: 0.1,
      pointRadius: 1
    });
    colorIdx++;
  }

  // Random reference baseline
  datasets.push({
    label: "Random Guess (AUC=0.5)",
    data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
    borderColor: "rgba(255, 255, 255, 0.2)",
    borderDash: [5, 5],
    borderWidth: 1,
    pointRadius: 0
  });

  AppState.rocChart = new Chart(ctx, {
    type: "line",
    data: { datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#94a3b8", font: { family: "Inter", size: 10 }, boxWidth: 12 }
        },
        tooltip: {
          backgroundColor: "rgba(15, 23, 42, 0.95)",
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: FPR=${ctx.parsed.x.toFixed(2)}, TPR=${ctx.parsed.y.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          type: "linear",
          min: 0,
          max: 1,
          title: { display: true, text: "False Positive Rate (1 - Specificity)", color: "#64748b" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          type: "linear",
          min: 0,
          max: 1.02,
          title: { display: true, text: "True Positive Rate (Sensitivity)", color: "#64748b" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        }
      }
    }
  });
}

function updateStaticRocImage() {
  const feat = AppState.activeFeatureSet;
  let filename = "roc_tf-idf_plus_properties.png";
  if (feat === "TF-IDF Only") filename = "roc_tf-idf_only.png";
  else if (feat === "Properties Only") filename = "roc_properties_only.png";

  const img = document.getElementById("roc-static-img");
  if (img) img.src = `/api/plots/${filename}?t=${Date.now()}`;
}

// ==========================================================================
// FEATURE INTELLIGENCE
// ==========================================================================

function renderFeatureImportanceChart(importances) {
  if (!importances || importances.length === 0) return;

  const ctx = document.getElementById("chart-feature-importance").getContext("2d");
  const labels = importances.map(i => i.feature);
  const dataVals = importances.map(i => +(i.importance * 100).toFixed(2));
  const colors = importances.map(i => i.is_structural ? "rgba(6, 182, 212, 0.85)" : "rgba(139, 92, 246, 0.7)");

  if (AppState.featureImportanceChart) {
    AppState.featureImportanceChart.destroy();
  }

  AppState.featureImportanceChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Feature Importance (%)",
        data: dataVals,
        backgroundColor: colors,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(15, 23, 42, 0.95)",
          callbacks: {
            label: (ctx) => `Signal Weight: ${ctx.parsed.x}%`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: "Signal Weight Contribution (%)", color: "#64748b" },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          ticks: { color: "#f8fafc", font: { family: "JetBrains Mono", size: 11 } },
          grid: { display: false }
        }
      }
    }
  });
}

function renderFeatureCatalog() {
  const container = document.getElementById("feature-catalog-grid");
  if (!container) return;
  container.innerHTML = "";

  for (const [key, item] of Object.entries(FEATURE_DEFINITIONS)) {
    const card = document.createElement("div");
    card.className = "catalog-card";
    card.innerHTML = `
      <div class="catalog-header">
        <span class="catalog-key">${key}</span>
        <span class="catalog-type">${item.type}</span>
      </div>
      <h4 class="catalog-title">${item.name}</h4>
      <p class="catalog-desc">${item.desc}</p>
      <div class="catalog-security-impact">
        <strong>Threat Rationale:</strong> ${item.impact}
      </div>
    `;
    container.appendChild(card);
  }
}

// ==========================================================================
// BATCH SCANNER LOGIC
// ==========================================================================

function handleBatchLoadPreset() {
  if (!AppState.samples || AppState.samples.length === 0) {
    showToast("Samples still loading, please wait...", "info");
    return;
  }
  showToast(`Loaded ${AppState.samples.length} standard test emails into batch queue.`, "info");
  handleBatchRun();
}

async function handleBatchRun() {
  if (!AppState.samples || AppState.samples.length === 0) {
    showToast("No test emails in queue.", "error");
    return;
  }

  const btn = document.getElementById("btn-batch-run");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Scanning...';

  const batchPayload = {
    emails: AppState.samples.map(s => ({
      id: s.id,
      text: s.body,
      sender: s.sender,
      recipient: s.recipient,
      subject: s.subject
    }))
  };

  try {
    const res = await fetch("/api/batch-analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(batchPayload)
    });

    if (!res.ok) throw new Error("Batch scan failed");

    const data = await res.json();
    AppState.batchResults = data.results || [];

    // Update Batch KPIs
    document.getElementById("batch-stats-grid").style.display = "grid";
    document.getElementById("batch-total").innerText = data.total_analyzed;
    document.getElementById("batch-phish").innerText = data.phishing_detected;
    document.getElementById("batch-phish-pct").innerText = `${data.phishing_rate_percent}% Flagged`;
    document.getElementById("batch-legit").innerText = data.legitimate_detected;
    document.getElementById("batch-avg-risk").innerText = `${data.average_risk_score}%`;

    // Render Batch Table
    renderBatchTable(data.results);
    document.getElementById("btn-export-csv").disabled = false;

    showToast(`Batch scan completed: ${data.phishing_detected} phishing, ${data.legitimate_detected} legitimate`, "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-play"></i> Run Batch Scan';
  }
}

function renderBatchTable(results) {
  const tbody = document.getElementById("tbody-batch");
  tbody.innerHTML = "";

  results.forEach((r, idx) => {
    const tr = document.createElement("tr");
    const isPhish = r.is_phishing;
    const flagsCount = r.red_flags ? r.red_flags.length : 0;

    tr.innerHTML = `
      <td class="code-font text-dim">${idx + 1}</td>
      <td>
        <span class="badge ${isPhish ? 'model-verdict-chip phish' : 'model-verdict-chip legit'}">
          ${r.verdict}
        </span>
      </td>
      <td><span class="flag-sev ${r.threat_level}">${r.threat_level}</span></td>
      <td><span class="metric-pill ${isPhish ? 'text-danger' : 'text-emerald'}">${r.risk_score}%</span></td>
      <td>
        <strong style="color: #fff; font-size: 0.85rem;">${escapeHtml(r.email_headers.Subject || 'Scan')}</strong>
        <div class="text-dim" style="font-size: 0.75rem;">${escapeHtml((r.extracted_text_snippet || '').slice(0, 60))}...</div>
      </td>
      <td class="code-font text-muted" style="font-size: 0.78rem;">${escapeHtml(r.email_headers.From || 'Unknown')}</td>
      <td>
        <span class="badge" style="background: rgba(255,255,255,0.05); color: ${flagsCount > 0 ? 'var(--danger)' : 'var(--emerald)'};">
          ${flagsCount} Flag${flagsCount !== 1 ? 's' : ''}
        </span>
      </td>
      <td>
        <button class="btn btn-ghost btn-xs" onclick="inspectBatchItem('${r.id}')" title="Inspect this item in Live Inspector">
          <i class="fa-solid fa-magnifying-glass"></i> View
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.inspectBatchItem = function(itemId) {
  const sample = AppState.samples.find(s => s.id === itemId);
  if (sample) {
    document.getElementById("tab-inspector").click();
    loadSampleIntoComposer(sample);
  }
};

function handleExportCsv() {
  if (!AppState.batchResults || AppState.batchResults.length === 0) return;

  const headers = ["ID", "Verdict", "Threat_Level", "Risk_Score", "Subject", "Sender", "Red_Flags_Count", "Phishing_Votes"];
  const rows = AppState.batchResults.map(r => [
    `"${r.id}"`,
    `"${r.verdict}"`,
    `"${r.threat_level}"`,
    r.risk_score,
    `"${(r.email_headers.Subject || '').replace(/"/g, '""')}"`,
    `"${(r.email_headers.From || '').replace(/"/g, '""')}"`,
    (r.red_flags || []).length,
    r.phishing_votes
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `phishshield_batch_report_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("CSV report exported successfully", "success");
}

// ==========================================================================
// RETRAINING
// ==========================================================================

async function handleStartRetrain() {
  const limit = parseInt(document.getElementById("retrain-sample-size").value);
  const btn = document.getElementById("btn-start-retrain");
  btn.disabled = true;

  const progressBox = document.getElementById("retrain-progress-box");
  progressBox.classList.remove("hidden");

  try {
    const res = await fetch("/api/retrain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ half_limit: limit })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Retrain request failed");
    }

    showToast(`Retraining started with ${limit} samples per class`, "info");
    pollRetrainStatus();
  } catch (err) {
    showToast(err.message, "error");
    btn.disabled = false;
  }
}

function pollRetrainStatus() {
  if (AppState.retrainPollInterval) clearInterval(AppState.retrainPollInterval);

  AppState.retrainPollInterval = setInterval(async () => {
    try {
      const res = await fetch("/api/retrain-status");
      if (!res.ok) return;
      const status = await res.json();

      const barFill = document.getElementById("retrain-bar-fill");
      const statusText = document.getElementById("retrain-status-text");
      const pctText = document.getElementById("retrain-pct-text");

      barFill.style.width = `${status.progress}%`;
      statusText.innerText = status.status_message;
      pctText.innerText = `${status.progress}%`;

      if (!status.is_training && status.progress === 100) {
        clearInterval(AppState.retrainPollInterval);
        document.getElementById("btn-start-retrain").disabled = false;
        showToast("Model retraining completed successfully!", "success");
        // Reload metrics
        loadSystemStatus();
        loadMetricsAndBenchmarks();
      } else if (!status.is_training && status.error) {
        clearInterval(AppState.retrainPollInterval);
        document.getElementById("btn-start-retrain").disabled = false;
        showToast(`Retraining failed: ${status.error}`, "error");
      }
    } catch (e) {
      console.error("Error polling retrain status:", e);
    }
  }, 1500);
}

// ==========================================================================
// TOAST NOTIFICATIONS
// ==========================================================================

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  let icon = "fa-circle-info";
  if (type === "success") icon = "fa-circle-check";
  else if (type === "error") icon = "fa-triangle-exclamation";

  toast.innerHTML = `
    <i class="fa-solid ${icon}"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Global window helpers for automated testing and dev console
window.switchTab = function(tabName) {
  const btn = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
  if (btn) btn.click();
};

window.loadSample = function(sampleId) {
  const sample = AppState.samples.find(s => s.id === sampleId);
  if (sample) loadSampleIntoComposer(sample, true);
};

window.runBatch = function() {
  handleBatchLoadPreset();
};
