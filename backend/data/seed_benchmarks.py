"""
Seed script to create validated precomputed benchmark datasets for Delhivery and India Macroeconomy.
These ensure instant evaluation out-of-the-box without requiring live paid API credentials.
"""

import json
from pathlib import Path
from backend.models.schemas import FactAtom, ReconciliationVerdict, VerdictType, DivergenceDimension


def generate_benchmarks():
    out_dir = Path(__file__).resolve().parent / "precomputed"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. DELHIVERY BENCHMARK DATASET
    # ==========================================
    delhivery_facts = [
        # Fact 1: Express Parcel FY21 (Prospectus)
        FactAtom(
            id="delhivery_fact_01",
            document_id="01-delhivery-prospectus-2022-excerpt.pdf",
            page_number=28,
            entity="Delhivery Limited",
            attribute="Express Parcel Shipment Volume",
            value_raw="577.06 million",
            value_numeric=577.06,
            unit="million shipments",
            temporal_anchor="FY21",
            scope="Consolidated Restated",
            quote="Our Express Parcel Services volume was 577.06 million orders in Fiscal 2021",
            context_window="Summary Financial and Operating Data table on Page 28",
            confidence=0.99
        ),
        # Fact 2: Express Parcel FY21 Retrospective (Annual Report FY24)
        FactAtom(
            id="delhivery_fact_02",
            document_id="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=12,
            entity="Delhivery Limited",
            attribute="Express Parcel Shipment Volume",
            value_raw="577.06 million",
            value_numeric=577.06,
            unit="million shipments",
            temporal_anchor="FY21",
            scope="Consolidated",
            quote="Express parcel volume delivered in FY21 stood at 577.06 million orders",
            context_window="Historical 5-year operating track record table on Page 12",
            confidence=0.99
        ),
        # Fact 3: Express Parcel FY24 (Annual Report FY24)
        FactAtom(
            id="delhivery_fact_03",
            document_id="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=4,
            entity="Delhivery Limited",
            attribute="Express Parcel Shipment Volume",
            value_raw="740 million",
            value_numeric=740.0,
            unit="million shipments",
            temporal_anchor="FY24",
            scope="Consolidated",
            quote="740 Mn Express parcel shipments delivered during the financial year ended March 31, 2024",
            context_window="Corporate Overview & Operational Highlights on Page 4",
            confidence=0.98
        ),
        # Fact 4: Express Parcel FY24 (Q4 Earnings Presentation)
        FactAtom(
            id="delhivery_fact_04",
            document_id="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=4,
            entity="Delhivery Limited",
            attribute="Express Parcel Shipment Volume",
            value_raw="740 million",
            value_numeric=740.0,
            unit="million shipments",
            temporal_anchor="FY24",
            scope="Consolidated",
            quote="FY24 Express Parcel volume reached 740M shipments",
            context_window="FY24 Full Year Operational Performance Summary on Page 4",
            confidence=0.98
        ),
        # Fact 5: PIN Codes Serviced in 2021 (Prospectus)
        FactAtom(
            id="delhivery_fact_05",
            document_id="01-delhivery-prospectus-2022-excerpt.pdf",
            page_number=47,
            entity="Delhivery Limited",
            attribute="PIN Codes Serviced",
            value_raw="17,488 PIN codes",
            value_numeric=17488.0,
            unit="pin codes",
            temporal_anchor="Dec 2021 (9M FY22)",
            scope="Serviced Reach (90.61% of India)",
            quote="serviced 17,488 PIN codes for the nine months period ended December 31, 2021, covering 90.61% of the 19,300 PIN codes in India",
            context_window="Business Strengths section, Paragraph 1 on Page 47",
            confidence=0.97
        ),
        # Fact 6: PIN Codes Covered in FY24 (Annual Report FY24)
        FactAtom(
            id="delhivery_fact_06",
            document_id="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=2,
            entity="Delhivery Limited",
            attribute="PIN Codes Serviced",
            value_raw="18,793 PIN codes",
            value_numeric=18793.0,
            unit="pin codes",
            temporal_anchor="FY24",
            scope="Network Reach",
            quote="18,793 (1) Pin codes covered across India",
            context_window="Key Metrics Dashboard on Page 2",
            confidence=0.98
        ),
        # Fact 7: FY24 Revenue from Operations Consolidated (Annual Report FY24)
        FactAtom(
            id="delhivery_fact_07",
            document_id="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=35,
            entity="Delhivery Limited",
            attribute="Revenue from Operations",
            value_raw="₹8,141.65 Crores",
            value_numeric=8141.65,
            unit="INR Crores",
            temporal_anchor="FY24",
            scope="Consolidated",
            quote="Revenue from operations for FY24 reached Rs. 8,141.65 Crores",
            context_window="Management Discussion and Analysis - Financial Performance on Page 35",
            confidence=0.99
        ),
        # Fact 8: FY24 Revenue from Operations Standalone (Annual Report FY24)
        FactAtom(
            id="delhivery_fact_08",
            document_id="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=112,
            entity="Delhivery Limited",
            attribute="Revenue from Operations",
            value_raw="₹7,858.91 Crores",
            value_numeric=7858.91,
            unit="INR Crores",
            temporal_anchor="FY24",
            scope="Standalone",
            quote="Standalone Revenue from operations stood at Rs. 7,858.91 Crores",
            context_window="Standalone Financial Statements - Statement of Profit and Loss on Page 112",
            confidence=0.99
        ),
        # Fact 9: Q4 FY24 Revenue from Operations (Q4 Presentation)
        FactAtom(
            id="delhivery_fact_09",
            document_id="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=5,
            entity="Delhivery Limited",
            attribute="Revenue from Operations",
            value_raw="₹2,076 Crores",
            value_numeric=2076.0,
            unit="INR Crores",
            temporal_anchor="Q4 FY24",
            scope="Consolidated",
            quote="Q4 FY24 Revenue from operations Rs 2,076 Cr",
            context_window="Q4 FY24 Financial Overview Slide on Page 5",
            confidence=0.98
        ),
        # Fact 10: Case 4 Trapped Fact - Naive Sign Inversion on Net Loss
        FactAtom(
            id="delhivery_fact_10",
            document_id="01-delhivery-prospectus-2022-excerpt.pdf",
            page_number=28,
            entity="Delhivery Limited",
            attribute="Restated Profit / (Loss) for the Year",
            value_raw="₹(4,157.43) million",
            value_numeric=4157.43,  # Naive positive parsing of parenthesized loss
            unit="INR million",
            temporal_anchor="FY21",
            scope="Restated Consolidated",
            quote="Restated Loss for the year (4,157.43) million",
            context_window="Summary Statement of Profit and Loss on Page 28",
            confidence=0.65,
            extraction_flags=["extraction_failure_flag"]
        ),
    ]

    delhivery_verdicts = [
        # Case 1: Corroboration
        ReconciliationVerdict(
            id="delh_v_01",
            topic="Delhivery Limited: Express Parcel Shipment Volume in FY21",
            verdict_type=VerdictType.CORROBORATED,
            fact_ids=["delhivery_fact_01", "delhivery_fact_02"],
            facts=[delhivery_facts[0], delhivery_facts[1]],
            summary="Identical Express Parcel volume of 577.06M confirmed across Prospectus and FY24 Annual Report.",
            explanation="Both the IPO Prospectus (2022) and the retrospective disclosures in the FY24 Annual Report report exactly 577.06 million shipments for FY21. Despite different publication dates, the retrospective historical accounting establishes direct corroboration.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Exact match on entity, attribute, temporal period (FY21), and numerical value (577.06M)."
        ),
        # Case 1: Corroboration (FY24 Volume)
        ReconciliationVerdict(
            id="delh_v_02",
            topic="Delhivery Limited: Express Parcel Shipment Volume in FY24",
            verdict_type=VerdictType.CORROBORATED,
            fact_ids=["delhivery_fact_03", "delhivery_fact_04"],
            facts=[delhivery_facts[2], delhivery_facts[3]],
            summary="Express Parcel volume of 740M for FY24 corroborated across Annual Report and Earnings Call.",
            explanation="Both the comprehensive FY24 Annual Report and the Q4 FY24 Investor Presentation independently report full-year Express Parcel volume of 740 million shipments.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Corroborated across primary statutory annual filing and investor relations presentation."
        ),
        # Case 3: Apparent Contradiction (Time)
        ReconciliationVerdict(
            id="delh_v_03",
            topic="Delhivery Limited: PIN Codes Reach",
            verdict_type=VerdictType.APPARENT_CONTRADICTION,
            fact_ids=["delhivery_fact_05", "delhivery_fact_06"],
            facts=[delhivery_facts[4], delhivery_facts[5]],
            summary="Apparent contradiction in PIN codes covered (17,488 vs 18,793) explained by network expansion over time.",
            explanation="Prospectus reports 17,488 PIN codes as of December 2021, whereas the FY24 Annual Report reports 18,793 PIN codes. This numerical discrepancy of +1,305 PIN codes is an apparent contradiction resolved by temporal drift: the company expanded its delivery footprint between 2021 and 2024.",
            divergence_dimension=DivergenceDimension.TIME,
            audit_notes="Resolved via temporal anchor: Dec 2021 vs FY24."
        ),
        # Case 3: Apparent Contradiction (Scope)
        ReconciliationVerdict(
            id="delh_v_04",
            topic="Delhivery Limited: FY24 Revenue from Operations",
            verdict_type=VerdictType.APPARENT_CONTRADICTION,
            fact_ids=["delhivery_fact_07", "delhivery_fact_08"],
            facts=[delhivery_facts[6], delhivery_facts[7]],
            summary="Apparent contradiction in FY24 revenue (₹8,141.65 Cr vs ₹7,858.91 Cr) resolved by Consolidated vs Standalone scope.",
            explanation="The FY24 Annual Report contains two different revenue figures for the same fiscal year. The epistemic engine isolates the scope qualifier: ₹8,141.65 Cr is the Consolidated figure (including operating subsidiaries such as Spoton Logistics), while ₹7,858.91 Cr is the Standalone figure of the parent company.",
            divergence_dimension=DivergenceDimension.SCOPE,
            audit_notes="Resolved via accounting perimeter: Consolidated vs Standalone."
        ),
        # Case 3: Apparent Contradiction (Time/Periodicity)
        ReconciliationVerdict(
            id="delh_v_05",
            topic="Delhivery Limited: Revenue from Operations Periodicity",
            verdict_type=VerdictType.APPARENT_CONTRADICTION,
            fact_ids=["delhivery_fact_07", "delhivery_fact_09"],
            facts=[delhivery_facts[6], delhivery_facts[8]],
            summary="Apparent contradiction in revenue (₹8,141.65 Cr vs ₹2,076 Cr) resolved by periodicity (Full Year vs Q4 Quarter).",
            explanation="The earnings presentation states revenue of ₹2,076 Cr while the annual report states ₹8,141.65 Cr. The reconciliation engine identifies that the former represents the 3-month fourth quarter (Q4 FY24) while the latter represents the 12-month annual period.",
            divergence_dimension=DivergenceDimension.TIME,
            audit_notes="Resolved via temporal periodicity: Annual vs Q4."
        ),
        # Case 4: Audited Extraction/Reasoning Failure
        ReconciliationVerdict(
            id="delh_v_06",
            topic="Delhivery Limited: Restated Net Loss FY21",
            verdict_type=VerdictType.EXTRACTION_FAILURE,
            fact_ids=["delhivery_fact_10"],
            facts=[delhivery_facts[9]],
            summary="Extraction / reasoning failure: Parenthesized negative number in financial table misattributed as positive profit.",
            explanation="The source prospectus on page 28 formats net loss as '(4,157.43)' million following Indian Accounting Standard (Ind AS) conventions where parentheses denote negative values. A naive text parser strips parentheses and emits a positive net profit of ₹4,157.43 million, causing a false contradiction with subsequent reports showing historic losses.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Handled by KnowledgeAuditor: detects parentheses in financial rows and enforces algebraic sign negation (-4,157.43)."
        ),
    ]

    # Save Delhivery benchmark
    with open(out_dir / "delhivery_benchmark.json", "w", encoding="utf-8") as f:
        json.dump({
            "dataset_name": "delhivery",
            "facts": [f.model_dump() for f in delhivery_facts],
            "verdicts": [v.model_dump() for v in delhivery_verdicts]
        }, f, indent=2)

    # ==========================================
    # 2. INDIA MACROECONOMY BENCHMARK DATASET
    # ==========================================
    macro_facts = [
        # Fact 1: Real GDP FY24 (RBI Annual Report)
        FactAtom(
            id="macro_fact_01",
            document_id="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=91,
            entity="Indian Economy",
            attribute="Real GDP Growth Rate",
            value_raw="9.2%",
            value_numeric=9.2,
            unit="%",
            temporal_anchor="2023-24 (FY24)",
            scope="Market Prices",
            quote="Real GDP at Market Prices (% change)* 2023-24: 9.2",
            context_window="Macroeconomic Appendix Table I.1: Real Economy on Page 91",
            confidence=0.99
        ),
        # Fact 2: Real GDP FY24 (IMF Article IV)
        FactAtom(
            id="macro_fact_02",
            document_id="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=44,
            entity="Indian Economy",
            attribute="Real GDP Growth Rate",
            value_raw="9.2%",
            value_numeric=9.2,
            unit="%",
            temporal_anchor="2023/24 (FY24)",
            scope="Market Prices",
            quote="Real GDP (at market prices) 2023/24: 9.2",
            context_window="Table 1: Selected Economic Indicators on Page 44",
            confidence=0.99
        ),
        # Fact 3: Real GDP FY25 (RBI Annual Report)
        FactAtom(
            id="macro_fact_03",
            document_id="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=91,
            entity="Indian Economy",
            attribute="Real GDP Growth Rate",
            value_raw="6.5%",
            value_numeric=6.5,
            unit="%",
            temporal_anchor="2024-25 (FY25)",
            scope="Market Prices",
            quote="Real GDP at Market Prices (% change)* 2024-25: 6.5",
            context_window="Macroeconomic Appendix Table I.1: Real Economy on Page 91",
            confidence=0.99
        ),
        # Fact 4: Real GDP FY25 (IMF Article IV)
        FactAtom(
            id="macro_fact_04",
            document_id="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=44,
            entity="Indian Economy",
            attribute="Real GDP Growth Rate",
            value_raw="6.5%",
            value_numeric=6.5,
            unit="%",
            temporal_anchor="2024/25 (FY25)",
            scope="Market Prices Est.",
            quote="Real GDP (at market prices) 2024/25 Est.: 6.5",
            context_window="Table 1: Selected Economic Indicators on Page 44",
            confidence=0.99
        ),
        # Fact 5: Forex Reserves March 2024 (Economic Survey)
        FactAtom(
            id="macro_fact_05",
            document_id="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=37,
            entity="Reserve Bank of India",
            attribute="Foreign Exchange Reserves",
            value_raw="USD 640.3 billion",
            value_numeric=640.3,
            unit="USD billion",
            temporal_anchor="End-March 2024",
            scope="Total Reserves",
            quote="Indias foreign exchange reserves stood at USD 640.3 billion as of the end of March 2024",
            context_window="External Sector Overview, Paragraph 1.58 on Page 37",
            confidence=0.98
        ),
        # Fact 6: Forex Reserves March 2024 (RBI Annual Report)
        FactAtom(
            id="macro_fact_06",
            document_id="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=90,
            entity="Reserve Bank of India",
            attribute="Foreign Exchange Reserves",
            value_raw="USD 651.5 billion",
            value_numeric=651.5,
            unit="USD billion",
            temporal_anchor="End-March 2024",
            scope="Total Reserves including valuation adjustments",
            quote="Foreign exchange reserves stood at USD 651.5 billion as at end-March 2024",
            context_window="Economic Review - External Sector on Page 90",
            confidence=0.98
        ),
        # Fact 7: Headline Inflation FY24 (Economic Survey)
        FactAtom(
            id="macro_fact_07",
            document_id="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=28,
            entity="Indian Economy",
            attribute="Consumer Price Inflation",
            value_raw="5.4%",
            value_numeric=5.4,
            unit="%",
            temporal_anchor="FY24",
            scope="Headline CPI",
            quote="Retail headline inflation, as measured by the change in the Consumer Price Index averaged 5.4 per cent in FY24",
            context_window="Prices and Inflation Section on Page 28",
            confidence=0.98
        ),
        # Fact 8: Core Inflation FY24 (Economic Survey)
        FactAtom(
            id="macro_fact_08",
            document_id="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=79,
            entity="Indian Economy",
            attribute="Consumer Price Inflation",
            value_raw="3.4%",
            value_numeric=3.4,
            unit="%",
            temporal_anchor="FY24",
            scope="Core CPI (Excluding Food & Fuel)",
            quote="Core inflation declined significantly to 3.4 per cent in FY24",
            context_window="Chart IV.4 Analysis on Page 79",
            confidence=0.98
        ),
        # Fact 9: Fiscal Deficit Projection (IMF Article IV)
        FactAtom(
            id="macro_fact_09",
            document_id="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=18,
            entity="Government of India",
            attribute="Fiscal Deficit (% of GDP)",
            value_raw="8.2% of GDP",
            value_numeric=8.2,
            unit="% of GDP",
            temporal_anchor="FY24",
            scope="General Government (Centre + States Consolidated)",
            quote="General government fiscal deficit remained elevated at 8.2 percent of GDP in FY2023/24",
            context_window="Fiscal Policy Review, Paragraph 12 on Page 18",
            confidence=0.97
        ),
        # Fact 10: Fiscal Deficit Target (Economic Survey)
        FactAtom(
            id="macro_fact_10",
            document_id="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=24,
            entity="Government of India",
            attribute="Fiscal Deficit (% of GDP)",
            value_raw="5.6% of GDP",
            value_numeric=5.6,
            unit="% of GDP",
            temporal_anchor="FY24",
            scope="Central Government",
            quote="Central Government fiscal deficit for FY24 stood at 5.6 per cent of GDP",
            context_window="Fiscal Developments and Budgetary Trends on Page 24",
            confidence=0.98
        ),
    ]

    macro_verdicts = [
        # Case 1: Corroboration (FY24 Real GDP)
        ReconciliationVerdict(
            id="macro_v_01",
            topic="Indian Economy: Real GDP Growth Rate FY24",
            verdict_type=VerdictType.CORROBORATED,
            fact_ids=["macro_fact_01", "macro_fact_02"],
            facts=[macro_facts[0], macro_facts[1]],
            summary="Real GDP growth of 9.2% for FY24 is corroborated across RBI Annual Report and IMF Article IV.",
            explanation="Both India's central bank (RBI) and the International Monetary Fund (IMF) confirm identical real GDP expansion of 9.2% at market prices for the fiscal year 2023-24.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Perfect alignment across national central bank data and multilateral institution surveillance."
        ),
        # Case 1: Corroboration (FY25 Real GDP)
        ReconciliationVerdict(
            id="macro_v_02",
            topic="Indian Economy: Real GDP Growth Rate FY25",
            verdict_type=VerdictType.CORROBORATED,
            fact_ids=["macro_fact_03", "macro_fact_04"],
            facts=[macro_facts[2], macro_facts[3]],
            summary="FY25 Real GDP growth of 6.5% corroborated between RBI and IMF.",
            explanation="Both the RBI Annual Report and IMF staff estimates project FY24/25 growth at 6.5%, corroborating the baseline growth trajectory.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Corroboration confirmed."
        ),
        # Case 2: Genuine / Likely Contradiction
        ReconciliationVerdict(
            id="macro_v_03",
            topic="Reserve Bank of India: Foreign Exchange Reserves (End-March 2024)",
            verdict_type=VerdictType.GENUINE_CONTRADICTION,
            fact_ids=["macro_fact_05", "macro_fact_06"],
            facts=[macro_facts[4], macro_facts[5]],
            summary="Genuine / likely contradiction in reported End-March 2024 Forex Reserves: USD 640.3B (Economic Survey) vs USD 651.5B (RBI).",
            explanation="Both reports cite the exact same institution (RBI), metric (Foreign Exchange Reserves), and balance sheet cutoff date (End-March 2024), but diverge by $11.2 Billion. While this stems from differing cut-off publication dates (provisional weekly BoP reporting vs audited balance sheet valuation adjustments), it functions as a genuine cross-document conflict in published official figures.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Flagged as Genuine / Likely Contradiction. Requires inspecting the RBI balance sheet notes to confirm currency revaluation reserves."
        ),
        # Case 3: Apparent Contradiction (Scope: Headline vs Core)
        ReconciliationVerdict(
            id="macro_v_04",
            topic="Indian Economy: Consumer Price Inflation FY24",
            verdict_type=VerdictType.APPARENT_CONTRADICTION,
            fact_ids=["macro_fact_07", "macro_fact_08"],
            facts=[macro_facts[6], macro_facts[7]],
            summary="Apparent contradiction in FY24 CPI inflation (5.4% vs 3.4%) resolved by Headline vs Core basket scope.",
            explanation="The Economic Survey reports both 5.4% and 3.4% for FY24 inflation. The epistemic engine reconciles the apparent contradiction through scope: 5.4% is the Headline CPI (which includes volatile food and energy prices), whereas 3.4% is Core CPI (which filters out food and fuel).",
            divergence_dimension=DivergenceDimension.SCOPE,
            audit_notes="Resolved via consumer price basket scope: Headline vs Core."
        ),
        # Case 3: Apparent Contradiction (Scope: General vs Central Government)
        ReconciliationVerdict(
            id="macro_v_05",
            topic="Government of India: Fiscal Deficit (% of GDP) FY24",
            verdict_type=VerdictType.APPARENT_CONTRADICTION,
            fact_ids=["macro_fact_09", "macro_fact_10"],
            facts=[macro_facts[8], macro_facts[9]],
            summary="Apparent contradiction in FY24 fiscal deficit (8.2% vs 5.6%) resolved by General Government vs Central Government perimeter.",
            explanation="IMF states the fiscal deficit is 8.2% of GDP, while the Economic Survey reports 5.6%. This stark difference is resolved by institutional perimeter: the Economic Survey measures the Central Government deficit alone, whereas the IMF reports the General Government deficit (consolidating Central Government + all 28 State Governments).",
            divergence_dimension=DivergenceDimension.SCOPE,
            audit_notes="Resolved via fiscal scope: General Government vs Central Government."
        ),
        # Case 4: Audited Extraction/Reasoning Failure
        ReconciliationVerdict(
            id="macro_v_06",
            topic="Indian Economy: GDP Deflator vs Real GDP Growth",
            verdict_type=VerdictType.EXTRACTION_FAILURE,
            fact_ids=["macro_fact_04"],
            facts=[macro_facts[3]],
            summary="Extraction / reasoning failure: Macroeconomic table column slippage between Real GDP and GDP Deflator.",
            explanation="On Page 64 of the IMF Article IV excerpt, a dense memorandum table places 'Real GDP growth (6.5%)' directly adjacent to 'Inflation (GDP deflator; 3.1%)'. A naive text regex or OCR column alignment matched the label 'Real GDP' with the adjacent deflator column value '3.1%', erroneously reporting that Indian GDP growth crashed to 3.1%.",
            divergence_dimension=DivergenceDimension.NONE,
            audit_notes="Handled by KnowledgeAuditor: detects table row-column boundary slippage and cross-checks with primary text narratives on Page 3 and Page 44."
        ),
    ]

    # Save Macro benchmark
    with open(out_dir / "macro_benchmark.json", "w", encoding="utf-8") as f:
        json.dump({
            "dataset_name": "india-macroeconomy",
            "facts": [f.model_dump() for f in macro_facts],
            "verdicts": [v.model_dump() for v in macro_verdicts]
        }, f, indent=2)

    print(f"Successfully generated precomputed benchmarks in {out_dir}")


if __name__ == "__main__":
    generate_benchmarks()
