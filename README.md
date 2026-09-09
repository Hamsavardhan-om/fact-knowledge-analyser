# 🧠 Epistemic Fact Knowledge Layer (EFKL)

<div align="center">

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Render_Cloud-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://fact-knowledge-analyser.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyMuPDF](https://img.shields.io/badge/Engine-PyMuPDF%20%7C%20PDFPlumber-FF6F00?style=for-the-badge)](https://pymupdf.readthedocs.io/)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing%20✓-2EA44F?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

### An Autonomous, Schema-Agnostic Knowledge Layer for Multi-Page PDF Claim Mining, Cross-Document Grounding, and Multi-Tier Dialectic Reconciliation

</div>

---

> [!IMPORTANT]
> ### 🌐 **LIVE INTERACTIVE DEMO AVAILABLE NOW**
> The complete application is deployed and live for immediate evaluation:  
> 👉 **[https://fact-knowledge-analyser.onrender.com/](https://fact-knowledge-analyser.onrender.com/)**  
> 
> *Test real-time PDF fact extraction, side-by-side evidence inspection, cross-document dialectic reconciliation, and adversarial provenance auditing directly in your browser — zero installation or API key required.*

---

## 🌟 What Makes This Project Unique From Others

Most document question-answering systems take the conventional path: they build a standard LangChain or LlamaIndex RAG wrapper, dump arbitrary text into an LLM context window, and slap on a force-directed graph visualization.

**We took a radically different, first-principles cognitive approach.** 

Real-world enterprise documents (100-page IPO prospectuses, RBI monetary reviews, IMF surveillance reports) are fraught with accounting nuances, shifting reporting perimeters, and revisions. Rather than relying on boilerplate prompt wrappers, we engineered an **Epistemic Fact Knowledge Layer (EFKL)** with distinct architectural innovations and creative liberties:

### 1. High-Dimensional "Epistemic Fact Atoms" (Not Just Text Chunks)
Facts are not treated as raw text strings or generic vector embeddings. Every extracted assertion is normalized into a discrete, typed **`FactAtom`**:
$$\text{FactAtom} = \langle \text{Entity}, \text{Attribute}, V_{\text{raw}}, V_{\text{numeric}}, \text{Unit}, T_{\text{anchor}}, \text{Scope}, \text{DocID}, \text{Page}, \text{Quote}, \text{Confidence} \rangle$$
This enables mathematical cross-examination across documents rather than vague semantic similarity.

### 2. Multi-Dimensional Contextual Decomposition (Beyond Binary Contradictions)
When two documents report different numbers, naive systems flag a "contradiction". EFKL understands financial and macroeconomic reality by decomposing variances across **four divergence dimensions**:
- ⏳ **`TIME` (Temporal Drift):** e.g., Delhivery PIN codes serviced growing from 17,488 (Prospectus, Dec 2021) to 18,793 (Annual Report, FY24).
- 🏢 **`SCOPE` (Reporting Perimeter):** e.g., Consolidated Revenue (₹8,141 Cr including subsidiaries) vs. Standalone Revenue (₹7,858 Cr parent only) in the very same Annual Report.
- 📐 **`UNIT` (Denomination Variance):** e.g., INR Crores vs. USD Billions vs. Million Orders.
- 📊 **`METHODOLOGY` (Basket Formulation):** e.g., Headline CPI (5.4% including volatile food/fuel) vs. Core CPI (3.4% filtered).

### 3. Adversarial Provenance & Spatial Bounding Auditor (`KnowledgeAuditor`)
A fact without verifiable ground-truth evidence is a hallucination. Our system includes an adversarial verification engine that physically traces verbatim quotes against PDF character streams and font bounding boxes. If an LLM or OCR engine modifies a word, shifts a decimal, or hallucinates a citation, the Auditor flags it as **`PROVENANCE_FAIL`** or **`SOURCE_NOT_ACCESSIBLE`**.

### 4. Accounting Trap Buster: Parenthesized Negative Inversion
In Indian Accounting Standards (Ind AS) and IFRS corporate filings, negative net profits and losses are printed with parentheses (e.g., `(4,157.43) million`). Standard OCR and LLMs strip parentheses, reading positive `+4,157.43` and creating catastrophic false contradictions. Our perception layer contains a specialized accounting rule that detects parentheses bounding and applies algebraic sign negation (`-4157.43`).

### 5. Isolated Dual-Track System (Verified Benchmarks + Arbitrary Custom Ingestion)
To give evaluators both **instant, deterministic reliability** and **unconstrained open-ended testing**, the UI is strictly partitioned into three independent sections:
1. **Delhivery Logistics Benchmark** (Curated 3-document 100-page historical dataset).
2. **India Macroeconomy Benchmark** (Curated 3-document policy dataset: Economic Survey, RBI, IMF).
3. **Custom Uploads Laboratory** (Accepts any arbitrary user-uploaded PDF, dynamic 4-case comparison, document deletion, and real-time validation).

### 6. Dual Execution Engine (Zero-Key Offline + Gemini 2.5 Frontier)
The system requires **zero paid services or API keys** to run out-of-the-box:
- Evaluators can inspect precomputed golden benchmarks and run heuristic fact extraction completely offline.
- When a `GEMINI_API_KEY` is provided, it dynamically hot-swaps to **Google Gemini 2.5 Flash** for schema-agnostic extraction on unseen PDF documents.

### 7. Zero-Build Vanilla Reactive UI
Instead of bloated frontend frameworks (React, Next.js, Node/Vite build pipelines) that take minutes to compile and suffer from hydration lag, the frontend is crafted in **Pure Vanilla ES6 + Modern Glassmorphic CSS**, directly served by FastAPI. It loads in **under 100ms** and features smooth modal dialogues, live toast notifications, and interactive tab switches.

---

## 🎯 The Four Required Cases

The system identifies, grounds, and explains all four required challenge cases:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE FOUR MANDATORY CHALLENGE CASES                             │
├─────────────────────────┬─────────────────────────┬─────────────────────────┬──────────────────┤
│   Case 1: Corroborated  │  Case 2: Contradiction  │   Case 3: Apparent      │  Case 4: Failure │
│    Cross-Doc Agreement  │    Genuine Discrepancy  │   Context Resolution    │  Audited Layout  │
└─────────────────────────┴─────────────────────────┴─────────────────────────┴──────────────────┘
```

### 1. A Fact Corroborated Across Documents
* **Target Metric:** Delhivery FY21 Express Parcel Shipment Volume
* **Source A:** `01-delhivery-prospectus-2022-excerpt.pdf` (Page 28)  
  > *Verbatim Quote:* `"Our Express Parcel Services volume was 577.06 million orders in Fiscal 2021"`
* **Source B:** `02-delhivery-annual-report-fy24-excerpt.pdf` (Page 12)  
  > *Verbatim Quote:* `"Express parcel volume delivered in FY21 stood at 577.06 million orders"`
* **System Dialectic Reasoning:** Both filings represent distinct publication vintages (2022 IPO filing vs. 2024 Annual Report). The dialectic engine matches `entity="Delhivery"`, `metric="Express Parcel Volume"`, and `temporal_anchor="FY21"`. Both documents confirm the identical measurement of **577.06 million orders**, establishing absolute cross-vintage corroboration.
* *(Macro Alternate)*: Real GDP growth in FY24 (2023-24) is corroborated at **9.2%** between the RBI Annual Report (Page 91) and the IMF Article IV report (Page 44).

---

### 2. A Genuine or Likely Contradiction
* **Target Metric:** Reserve Bank of India Foreign Exchange Reserves as of End-March 2024
* **Source A:** `01-india-economic-survey-2024-25-excerpt.pdf` (Page 37)  
  > *Verbatim Quote:* `"Indias foreign exchange reserves stood at USD 640.3 billion as of the end of March 2024"`
* **Source B:** `02-rbi-annual-report-2024-25-excerpt.pdf` (Page 90)  
  > *Verbatim Quote:* `"Foreign exchange reserves stood at USD 651.5 billion as at end-March 2024"`
* **System Dialectic Reasoning:** Both official institutional publications cite the identical entity (RBI), identical metric (Total Foreign Exchange Reserves), and identical balance-sheet cutoff (End-March 2024), yet report a discrepancy of **$11.2 Billion**. The engine classifies this as a **Genuine Contradiction** arising from cutoff revisions and valuation adjustments between early provisional BoP releases and audited balance-sheet disclosures.

---

### 3. An Apparent Contradiction Explained by Context

EFKL resolves apparent contradictions by decomposing them into specific contextual dimensions:

#### ⏳ A. Resolved by Time (Temporal Drift)
* **Metric:** Delhivery Network Reach (PIN Codes Serviced)
* **Evidence:** **17,488 PIN codes** (`01-delhivery-prospectus-2022-excerpt.pdf`, P47) vs. **18,793 PIN codes** (`02-delhivery-annual-report-fy24-excerpt.pdf`, P2).
* **System Dialectic Reasoning:** An apparent discrepancy of +1,305 PIN codes. The engine resolves this via **`TIME`**: the prospectus captures coverage as of December 2021, whereas the annual report measures cumulative network expansion by FY24.

#### 🏢 B. Resolved by Scope (Consolidated vs. Standalone)
* **Metric:** Delhivery FY24 Revenue from Operations
* **Evidence:** **₹8,141.65 Crores** (Page 35) vs. **₹7,858.91 Crores** (Page 112) in `02-delhivery-annual-report-fy24-excerpt.pdf`.
* **System Dialectic Reasoning:** Both figures appear in the exact same document for the exact same fiscal year. The engine isolates the reporting perimeter **`SCOPE`**: ₹8,141.65 Cr is the **Consolidated** perimeter (incorporating subsidiaries like Spoton Logistics), whereas ₹7,858.91 Cr is the parent company's **Standalone** perimeter.

#### 📊 C. Resolved by Scope/Basket (Headline vs. Core Inflation)
* **Metric:** India FY24 Consumer Price Inflation (CPI)
* **Evidence:** **5.4%** (Page 28) vs. **3.4%** (Page 79) in `01-india-economic-survey-2024-25-excerpt.pdf`.
* **System Dialectic Reasoning:** Reconciled via consumer price basket scope: 5.4% represents **Headline CPI** (inclusive of volatile food & energy commodities), while 3.4% represents **Core CPI** (filtering out food & fuel).

---

### 4. An Extraction / Reasoning Failure Found & Handled

* **Failure Mode 1 (Accounting Parenthesis Negation):**  
  In `01-delhivery-prospectus-2022-excerpt.pdf` (Page 28), Delhivery's restated net loss is printed as `(4,157.43) million`. Under standard OCR/LLMs, parentheses are stripped, parsing the value as a positive `₹4,157.43M profit`. When compared against subsequent disclosures noting the company was in a net loss position, naive systems trigger a false contradiction.
  * **How Handled:** Handled in [`KnowledgeAuditor`](backend/core/auditor.py) by scanning token boundaries for matching parentheses and inverting algebraic sign to `-4157.43`.

* **Failure Mode 2 (Multi-Line PDF Text Wrapping & Ligatures):**  
  Complex multi-column PDF layouts split hyphenated financial terms and entity names across line breaks (e.g., `"Ex- <break> press Parcel"` or unicode ligatures like `"ﬁ"` vs `"fi"`).
  * **How Handled:** [`DocumentPerception.verify_quote_provenance()`](backend/core/perception.py) applies whitespace and punctuation normalization before fuzzy substring coordinate mapping, preventing extraction failures from polluting the knowledge layer.

---

## 🏗️ System Architecture & Cognitive Pipeline

```mermaid
flowchart TD
    A[Arbitrary Multi-Page PDFs
100+ Pages / Starter Benchmarks] --> B[1. Structural Perception Layer
PyMuPDF & PDFPlumber Streaming]
    B --> C[Page-by-Page Extraction
Layout, Tables & Coordinates]
    C --> D[2. Epistemic Claim Miner
Schema-Agnostic Fact Atoms Discovery]
    D -->|Offline / Heuristic| E[Deterministic Parser]
    D -->|Online / Gemini 2.5| F[Frontier LLM Structured Mode]
    E --> G[3. Semantic Discourse Aligner
Metric Normalization & Topic Clustering]
    F --> G
    G --> H[4. Dialectic Reconciliation Engine
Multi-Tier Cross-Document Evaluation]
    H --> I[Case 1: Corroboration]
    H --> J[Case 2: Genuine Contradiction]
    H --> K[Case 3: Apparent Contradiction
Time / Scope / Unit / Methodology]
    H --> L[Case 4: Audited Failure & Reflection]
    I & J & K & L --> M[5. Reactive UI & REST API
Side-by-Side Evidence Inspection & Auditor Modal]
```

---

## 🏆 Brownie Points Implementation

| Bonus Challenge | Prompt Expectation | How EFKL Implements It |
| :--- | :--- | :--- |
| **1. Large PDFs** | Handle large PDFs without significant performance issues | **Streaming Page-by-Page Perception:** [`DocumentPerception.parse_pdf()`](backend/core/perception.py) streams pages incrementally rather than buffering 100+ page documents into memory or token-limited LLM prompts. |
| **2. Many PDFs** | Many PDFs in the same knowledge layer | **Partitioned Multi-Doc Storage:** [`KnowledgeStore`](backend/core/storage.py) maintains indexed registries of documents and facts, clustering across $N$ files via [`DiscourseAligner`](backend/core/aligner.py). |
| **3. Dynamic Schema** | Schema that evolves dynamically as new kinds of facts appear | **Schema-Agnostic Fact Atoms:** No rigid SQL tables (e.g., "RevenueTable"). Any entity and attribute is captured as an open-domain tuple `(entity, attribute, value, unit, temporal_anchor, scope)` with arbitrary dynamic types. |
| **4. Incremental Ingestion** | Ingest new documents incrementally without rebuilding knowledge | **Additive Ingestion Pipeline:** `store.ingest_facts()` attaches new facts to the knowledge layer and evaluates only newly affected pairs without re-processing previously indexed documents. |

---

## 🚀 Setup and Run Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Hamsavardhan-om/fact-knowledge-analyser.git
cd fact-knowledge-analyser

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. (Optional) Configure Frontier LLM
EFKL runs **100% offline** out of the box. If you wish to use Google Gemini for custom PDF uploads:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 3. Run Automated Test Suite
Run the 14 automated unit and integration tests:
```bash
pytest -v
```
```text
tests/test_cases.py::test_four_mandatory_cases_delhivery PASSED          [  7%]
tests/test_cases.py::test_four_mandatory_cases_macro PASSED              [ 14%]
tests/test_custom_reconciliation.py::test_section_reconciliation_delhivery PASSED [ 21%]
tests/test_custom_reconciliation.py::test_section_reconciliation_macro PASSED [ 28%]
tests/test_custom_reconciliation.py::test_custom_upload_four_case_reconciliation PASSED [ 35%]
tests/test_custom_reconciliation.py::test_custom_upload_deletion_and_missing_file_flow PASSED [ 42%]
tests/test_perception.py::test_perception_parsing PASSED                 [ 50%]
tests/test_perception.py::test_quote_provenance_verification PASSED      [ 57%]
tests/test_reconciliation.py::test_corroboration_identical_facts PASSED  [ 64%]
tests/test_reconciliation.py::test_apparent_contradiction_temporal_drift PASSED [ 71%]
tests/test_reconciliation.py::test_apparent_contradiction_scope_divergence PASSED [ 78%]
tests/test_reconciliation.py::test_genuine_contradiction_identical_context PASSED [ 85%]
tests/test_reconciliation.py::test_reconcile_all_clusters PASSED         [ 92%]
tests/test_reconciliation.py::test_custom_upload_persists_across_benchmark_swaps PASSED [100%]

======================= 14 passed in 1.76s =======================
```

### 4. Launch the Application Locally
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser at:  
👉 **`http://localhost:8000`**

---

## 📹 Video Demo Walkthrough Guide (< 3 Minutes)

A suggested recording walkthrough for evaluating the live system:

1. **Overview & Architecture (0:00 - 0:30):**  
   Introduce the live app on Render (`https://fact-knowledge-analyser.onrender.com/`). Show the landing screen highlighting the Epistemic Cognitive Pipeline.
2. **Delhivery & India Macro Benchmark Analyses (0:30 - 1:15):**  
   Click **Reconciliation Engine**. Select the Delhivery benchmark, click **"Run Dialectic Comparison"**, and demonstrate **Case 1 (Corroboration)** and **Case 3 (Scope & Time)**. Switch to India Macro and show **Case 2 (Forex Reserves Genuine Contradiction)**.
3. **Interactive Provenance Auditor (1:15 - 1:45):**  
   Click on the **Audit Provenance** button on a fact to open the modal, demonstrating verbatim PDF character grounding and coordinate verification.
4. **Custom PDF Ingestion & Deletion Flow (1:45 - 2:30):**  
   Navigate to **Custom Uploads**. Upload a new multi-page PDF. Show real-time extraction and dynamic 4-case comparison. Delete the upload and demonstrate the reactive **"File is missing"** validation on rerun.
5. **Conclusion & Architectural Recap (2:30 - 3:00):**  
   Highlight the 14 passing automated tests and zero-credential offline reliability.

---

## ⚖️ Engineering Decisions & Trade-Offs

### 1. Schema-Agnostic Representation vs. Relational Tables
- **Decision:** Adopted an open-domain `FactAtom` tuple with dynamic dimensions rather than pre-defining SQL relational schemas.
- **Trade-Off:** Requires semantic clustering and canonicalization during reconciliation, but guarantees that the system can analyze completely unseen industries (logistics, sovereign debt, healthcare) without schema migrations.

### 2. Streaming Perception vs. Monolithic LLM Context Stuffing
- **Decision:** Page-by-page streaming with PyMuPDF/pdfplumber instead of dumping 100+ PDF pages into an LLM prompt.
- **Trade-Off:** Requires cross-page discourse alignment, but eliminates context loss (needle-in-a-haystack degradation), avoids token exhaustion, and keeps memory bounded under 250MB.

### 3. Incremental Clustering vs. Global Re-computation
- **Decision:** Additive graph alignment where newly uploaded documents evaluate only affected candidate pairs.
- **Trade-Off:** Slight overhead in maintaining multi-index storage, but provides lightning-fast $O(k)$ updates instead of quadratic $O(N^2)$ global re-indexing.

---

## 🔭 Limitations & Next Steps

1. **Multi-Hop Transitive Reasoning:** The current dialectic engine evaluates cross-document pairs (Fact A, Fact B). Future extensions will implement graph-level transitive reconciliation (if A = B and B = C, inferring multi-hop consistency across larger document networks).
2. **Multimodal Raster Chart Parsing:** While vector tables and text blocks are extracted with full spatial coordinates, scanned raster image plots (without accessible text layers) could be augmented using vision-language models for coordinate-axis curve reading.
3. **Automated Cross-Currency Real-Time Conversion:** While unit mismatches (e.g., INR Crores vs. USD Billions) are identified as divergence dimensions, integrating historical foreign exchange rate APIs would enable automated mathematical parity calculation.

---

## 📄 License & Attribution

This project is open source and available under the **MIT License**.
