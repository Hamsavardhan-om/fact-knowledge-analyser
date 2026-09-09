# Epistemic Fact Knowledge Layer (EFKL)

> **Epistemic Fact Knowledge Layer & Dialectic Reconciliation Engine**  
> An autonomous, schema-agnostic knowledge layer that extracts grounded facts from multi-page documents, links assertions to verbatim source evidence, and reconciles cross-document relationships through multi-tier dialectic reasoning.

---

## Table of Contents
1. [Overview & Philosophy](#overview--philosophy)
2. [The Four Required Cases](#the-four-required-cases)
3. [Architecture & Pipeline](#architecture--pipeline)
4. [Setup and Run Instructions](#setup-and-run-instructions)
5. [Approach, Decisions & Trade-Offs](#approach-decisions--trade-offs)
6. [Limitations and Next Steps](#limitations-and-next-steps)
7. [Video Demo Guide](#video-demo-guide)
8. [Additional Notes](#additional-notes)

---

## Overview & Philosophy

Building a real-world **Fact Knowledge Layer** over arbitrary institutional documents (annual reports, prospectus filings, IMF economic reviews) is notoriously challenging. Naive LLM prompt wrappers fail because:
- They hallucinate numbers and lose track of page provenance.
- They choke on 100-page disclosures and complex financial tables.
- They treat all conflicting numbers as "contradictions" when they are actually differences in **time** (FY21 vs FY24), **accounting scope** (Consolidated vs Standalone), or **price methodology** (Headline vs Core CPI).

**Our Mantra:** Stay unique, grounded, and driven by first-principles cognitive architecture rather than boilerplate wrappers or rigid fine-tuned models.

EFKL decomposes documents into **Epistemic Fact Atoms** equipped with temporal, dimensional, and verbatim provenance anchors, cross-examining them through an **Audited Dialectic Engine**.

---

## The Four Required Cases

The system natively identifies and explains all four required cases across both starter datasets (**Delhivery** and **India Macroeconomy**):

### 1. A Fact Corroborated Across Documents
* **Case:** Delhivery FY21 Express Parcel Shipment Volume
* **Source A:** `01-delhivery-prospectus-2022-excerpt.pdf` (Page 28)  
  *Quote:* `"Our Express Parcel Services volume was 577.06 million orders in Fiscal 2021"`
* **Source B:** `02-delhivery-annual-report-fy24-excerpt.pdf` (Page 12)  
  *Quote:* `"Express parcel volume delivered in FY21 stood at 577.06 million orders"`
* **System Reasoning:** Both documents state an identical measurement of **577.06 million shipments** under the exact same temporal period (FY21) and consolidated scope, corroborating historical disclosures despite different publication vintages.
* *(Macro Alternate)*: Real GDP growth in FY24 (2023-24) is corroborated at **9.2%** between the RBI Annual Report (Page 91) and the IMF Article IV report (Page 44).

---

### 2. A Genuine or Likely Contradiction
* **Case:** Reserve Bank of India Foreign Exchange Reserves as of End-March 2024
* **Source A:** `01-india-economic-survey-2024-25-excerpt.pdf` (Page 37)  
  *Quote:* `"Indias foreign exchange reserves stood at USD 640.3 billion as of the end of March 2024"`
* **Source B:** `02-rbi-annual-report-2024-25-excerpt.pdf` (Page 90)  
  *Quote:* `"Foreign exchange reserves stood at USD 651.5 billion as at end-March 2024"`
* **System Reasoning:** Both official institutional publications cite the identical entity (RBI), identical metric (Total Foreign Exchange Reserves), and identical balance-sheet cutoff (End-March 2024), yet report a discrepancy of **$11.2 Billion**. The dialectic engine flags this as a **Genuine Contradiction** arising from cutoff revisions and valuation adjustments between early provisional BoP releases and audited balance-sheet disclosures.

---

### 3. An Apparent Contradiction Explained by Context
EFKL decomposes apparent contradictions across three dimensions:

#### A. Resolved by Time (Temporal Drift)
* **Facts:** Delhivery PIN Codes Serviced: **17,488** (`01-delhivery-prospectus-2022-excerpt.pdf`, P47) vs **18,793** (`02-delhivery-annual-report-fy24-excerpt.pdf`, P2).
* **System Reasoning:** The +1,305 PIN codes variance is an apparent contradiction resolved by temporal drift: the prospectus captures coverage as of December 2021, whereas the annual report measures cumulative network expansion by FY24.

#### B. Resolved by Scope (Consolidated vs Standalone)
* **Facts:** Delhivery FY24 Revenue from Operations: **₹8,141.65 Crores** (P35) vs **₹7,858.91 Crores** (P112).
* **System Reasoning:** Both figures appear in the same annual report for the same year. The engine isolates the scope qualifier: ₹8,141.65 Cr is the **Consolidated** perimeter (incorporating subsidiaries like Spoton Logistics), whereas ₹7,858.91 Cr is the parent company's **Standalone** perimeter.

#### C. Resolved by Scope/Basket (Headline vs Core Inflation)
* **Facts:** India FY24 CPI Inflation: **5.4%** (P28) vs **3.4%** (P79) in `01-india-economic-survey-2024-25-excerpt.pdf`.
* **System Reasoning:** Reconciled via consumer price basket scope: 5.4% represents **Headline CPI** (inclusive of volatile food & energy commodities), while 3.4% represents **Core CPI** (filtering out food & fuel).

---

### 4. An Extraction / Reasoning Failure & How It Was Handled
* **The Failure:** Parenthesized negative values in Indian corporate balance sheets.
* **Context:** In `01-delhivery-prospectus-2022-excerpt.pdf` (Page 28), Delhivery's restated net loss is printed as `(4,157.43) million`. Under Ind AS accounting standards, parentheses signify negative numbers.
* **Failure Mode:** Standard OCR / LLM extractors strip parentheses and extract positive `₹4,157.43 million` in profit. When compared with subsequent reports stating the company operated at a loss, the system generates a catastrophic false contradiction!
* **How Handled / Improved:**
  - Built an adversarial **KnowledgeAuditor** (`backend/core/auditor.py`) that checks financial line items for bounding parentheses and enforces algebraic sign negation (`-4157.43`).
  - Added verbatim bounding box verification (`verify_quote_provenance`) so claims that cannot be traced to exact PDF coordinates are quarantined.

---

## Architecture & Pipeline

```
                       ┌─────────────────────────┐
                       │  Arbitrary Multi-Page   │
                       │          PDFs           │
                       └────────────┬────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ 1. Structural Perception Layer (perception.py)         │
       │ - PyMuPDF-based streaming extraction                   │
       │ - Layout awareness (tabular pipes vs narrative prose)  │
       │ - Exact page coordinate tracking & quote bounding      │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ 2. Epistemic Claim Miner (extractor.py)                │
       │ - Schema-agnostic decomposition into Fact Atoms        │
       │ - Discovers: entity, attribute, value, unit,           │
       │   temporal anchor, scope qualifiers, verbatim quote    │
       │ - Supports Gemini 2.5 structured mode + heuristic parser│
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ 3. Semantic Discourse Aligner (aligner.py)             │
       │ - Topic clustering via N-gram affinity & canonicalizer │
       │ - Incremental: attaches new PDFs without re-indexing   │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ 4. Dialectic Reconciliation Engine (reconciler.py)     │
       │ - Tier 1: Corroboration Engine                         │
       │ - Tier 2: Contextual Decomposition (Time, Scope, Unit) │
       │ - Tier 3: Genuine Contradiction Detector               │
       │ - Tier 4: Adversarial Error Auditor (auditor.py)       │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ 5. Reactive UI Dashboard & REST API (main.py)          │
       │ - Side-by-side evidence inspection                     │
       │ - Real-time quote provenance auditor                   │
       │ - Dynamic 4-Case filter tabs                           │
       └────────────────────────────────────────────────────────┘
```

---

## Setup and Run Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed
- Virtual environment support

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone <your-repo-url>
cd Fact_knowledge_layer

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
EFKL ships with **full offline execution** and precomputed golden benchmark datasets so evaluators can test immediately without any API key or paid service.

If you want to use the live Gemini 2.5 Flash model for newly uploaded PDFs, set your key:
```bash
# In .env or shell:
export GEMINI_API_KEY="your_api_key_here"
# On Windows PowerShell:
$env:GEMINI_API_KEY="your_api_key_here"
```

### 3. Run Automated Verification Tests
```bash
pytest -v
```
*All 8 automated tests verify PDF parsing, dialectic reconciliation, and all 4 mandatory cases.*

### 4. Launch the Web Application
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## Approach, Decisions & Trade-Offs

### 1. Schema-Agnostic vs Fixed Schema
* **Decision:** We refused to hardcode entities (`Delhivery`, `RBI`) or attributes (`Revenue`, `GDP`).
* **Trade-off:** Requires a flexible `FactAtom` structure with semantic discourse alignment (`aligner.py`), but guarantees the system can accept completely unseen PDFs (e.g. healthcare, semiconductor earnings, climate reports) without code changes.

### 2. Large PDFs (100+ Pages)
* **Decision:** Handled through **page-by-page streaming perception** (`DocumentPerception`) rather than stuffing entire multi-megabyte PDF texts into an LLM context window.
* **Trade-off:** Slightly more localized extraction per page, but eliminates context loss, avoids token exhaustion, and keeps memory bounded.

### 3. Incremental Ingestion
* **Decision:** New documents are ingested additively into `KnowledgeStore`. Newly mined facts are matched against existing discourse topics or seed new ones, re-evaluating reconciliation only across affected pairs.
* **Trade-off:** Maintains fast $O(k)$ updates rather than $O(N^2)$ global reprocessing.

---

## Limitations and Next Steps

1. **Multi-hop Transitive Reconciliation:** Currently, the dialectic engine reconciles pairwise claims $(F_A, F_B)$. Next, we plan to implement graph-level transitive reasoning (e.g., if $A = B$ and $B = C$, verifying transitivity across multi-document chains).
2. **Chart/Image OCR:** PyMuPDF extracts vector text and native tables. For scanned bitmap charts (e.g. raster graphs without accessible text layers), integrating an OCR-vision model (like Gemini Multimodal Flash) would extract data points directly from chart coordinate axes.
3. **Automated Unit Conversion Engine:** While the system identifies unit mismatches (e.g. INR Crores vs USD Millions), integrating dynamic foreign-exchange rate APIs would compute mathematical equivalence on the fly.

---

## Video Demo Guide

A 3-minute video walk-through demonstrating:
1. **System Overview & Architecture:** Showing the reactive dashboard.
2. **Case 1 (Corroboration):** Delhivery FY21 Express Parcel Volume (577.06M) verified across Prospectus and FY24 Annual Report.
3. **Case 2 (Genuine Contradiction):** Forex Reserves discrepancy ($640.3B vs $651.5B) flagged between Economic Survey and RBI.
4. **Case 3 (Apparent Contradiction):** Demonstrating Time (PIN codes 17,488 vs 18,793) and Scope (Consolidated vs Standalone revenue).
5. **Case 4 (Audited Failure):** Using the **Quote Provenance Auditor** to inspect parenthesized loss sign inversion.
6. **Live PDF Ingestion:** Dropping a new PDF into the UI and seeing the knowledge layer update live.

---

## Additional Notes
- Evaluators can switch seamlessly between the **Delhivery Logistics** and **India Macroeconomy** datasets with a single click in the top navbar.
- All code follows clean Python standards with typed Pydantic models.
