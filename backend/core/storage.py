"""
In-memory and disk persistence layer for the Epistemic Fact Knowledge Layer.
Supports dynamic schema updates and incremental document ingestion.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from backend.models.schemas import (
    FactAtom,
    ReconciliationVerdict,
    DocumentSummary,
    KnowledgeLayerState,
    VerdictType,
)
from backend.core.aligner import DiscourseAligner
from backend.core.reconciler import DialecticReconciler
from backend.config import STORAGE_FILE, BENCHMARKS_DIR, CUSTOM_UPLOADS_FILE, UPLOADS_DIR


class KnowledgeStore:
    def __init__(self):
        self.documents: Dict[str, DocumentSummary] = {}
        self.facts: Dict[str, FactAtom] = {}
        self.verdicts: List[ReconciliationVerdict] = []
        self.custom_documents: Dict[str, DocumentSummary] = {}
        self.custom_facts: Dict[str, FactAtom] = {}
        self.custom_verdicts: List[ReconciliationVerdict] = []
        self.aligner = DiscourseAligner()
        self.reconciler = DialecticReconciler()
        self._load_custom_uploads()
        self._load_from_disk()
        if not self.custom_documents:
            self._auto_restore_raw_uploads()

    def _load_custom_uploads(self):
        """Loads user-uploaded documents and facts from dedicated custom_uploads.json"""
        if CUSTOM_UPLOADS_FILE.exists():
            try:
                with open(CUSTOM_UPLOADS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for doc in data.get("documents", []):
                        d = DocumentSummary(**doc)
                        d.is_benchmark = False
                        self.custom_documents[d.document_id] = d
                    for fact in data.get("facts", []):
                        fa = FactAtom(**fact)
                        self.custom_facts[fa.id] = fa
                        if fa.document_id in self.custom_documents:
                            self.custom_documents[fa.document_id].facts.append(fa)
            except Exception as e:
                print(f"[KnowledgeStore] Error loading custom_uploads.json: {e}")

    def _save_custom_uploads(self):
        """Persists user-uploaded documents and facts into custom_uploads.json"""
        try:
            data = {
                "documents": [d.model_dump() for d in self.custom_documents.values()],
                "facts": [f.model_dump() for f in self.custom_facts.values()]
            }
            with open(CUSTOM_UPLOADS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[KnowledgeStore] Error saving custom_uploads.json: {e}")

    def _auto_restore_raw_uploads(self):
        """Scans raw_uploads for user-uploaded PDFs and extracts facts if not already present."""
        from backend.core.perception import DocumentPerception
        from backend.core.extractor import EpistemicExtractor

        if not UPLOADS_DIR.exists():
            return

        extractor = EpistemicExtractor()
        for pdf_path in UPLOADS_DIR.glob("*.pdf"):
            if "delhivery" in pdf_path.name.lower() or "macro" in pdf_path.name.lower():
                continue
            if pdf_path.name in self.custom_documents:
                continue
            try:
                pages = DocumentPerception.parse_pdf(pdf_path)
                facts = []
                for p in pages:
                    p_facts = extractor.extract_from_page(p)
                    facts.extend(p_facts)

                doc_summary = DocumentSummary(
                    document_id=pdf_path.name,
                    total_pages=len(pages),
                    extracted_facts_count=len(facts),
                    file_size_bytes=pdf_path.stat().st_size,
                    upload_timestamp=datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
                    is_benchmark=False
                )
                self.custom_documents[doc_summary.document_id] = doc_summary
                for f in facts:
                    self.custom_facts[f.id] = f
                print(f"[KnowledgeStore] Auto-restored upload: {pdf_path.name} with {len(facts)} facts")
            except Exception as e:
                print(f"[KnowledgeStore] Failed to auto-restore {pdf_path.name}: {e}")

        if self.custom_documents:
            self._save_custom_uploads()

    def _load_from_disk(self):
        if STORAGE_FILE.exists():
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.active_benchmark = data.get("active_benchmark", "delhivery")
                    for doc in data.get("documents", []):
                        d = DocumentSummary(**doc)
                        if d.is_benchmark:
                            self.documents[d.document_id] = d
                    for fact in data.get("all_facts", []):
                        fa = FactAtom(**fact)
                        if fa.document_id in self.documents:
                            self.facts[fa.id] = fa
                    for v in data.get("verdicts", []):
                        self.verdicts.append(ReconciliationVerdict(**v))
            except Exception as e:
                print(f"[KnowledgeStore] Error loading storage.json: {e}")

    def save_to_disk(self):
        state = self.get_state()
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2)
        self._save_custom_uploads()

    def load_benchmark(self, dataset_name: str) -> bool:
        """
        Loads precomputed golden benchmarks (delhivery or india-macroeconomy).
        Contains strictly ONLY the 3 pre-ingested benchmark documents.
        Custom uploads remain safely isolated in self.custom_documents.
        """
        filename = "delhivery_benchmark.json" if "delhi" in dataset_name.lower() else "macro_benchmark.json"
        bench_file = BENCHMARKS_DIR / filename
        if not bench_file.exists():
            return False

        with open(bench_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Strictly clear active benchmark store - do NOT merge custom uploads here!
        self.documents.clear()
        self.facts.clear()
        self.verdicts.clear()

        # Metadata dictionary for exact page counts and file sizes
        doc_meta = {
            "01-delhivery-prospectus-2022-excerpt.pdf": {"pages": 100, "size": 1597612},
            "02-delhivery-annual-report-fy24-excerpt.pdf": {"pages": 100, "size": 6679023},
            "03-delhivery-q4-fy24-earnings-presentation.pdf": {"pages": 27, "size": 1988328},
            "01-india-economic-survey-2024-25-excerpt.pdf": {"pages": 89, "size": 3920928},
            "02-rbi-annual-report-2024-25-excerpt.pdf": {"pages": 100, "size": 1507769},
            "03-imf-india-2025-article-iv-excerpt.pdf": {"pages": 95, "size": 4305245},
        }

        self.active_benchmark = "delhivery" if "delhi" in dataset_name.lower() else "india-macroeconomy"

        # Add benchmark facts and documents
        for f_data in data.get("facts", []):
            f = FactAtom(**f_data)
            self.facts[f.id] = f
            if f.document_id not in self.documents:
                meta = doc_meta.get(f.document_id, {"pages": 100, "size": 1024 * 1024})
                self.documents[f.document_id] = DocumentSummary(
                    document_id=f.document_id,
                    total_pages=meta["pages"],
                    extracted_facts_count=0,
                    file_size_bytes=meta["size"],
                    upload_timestamp=datetime.now().isoformat(),
                    is_benchmark=True,
                    benchmark_name="delhivery" if "delhi" in dataset_name.lower() else "india-macroeconomy"
                )
            self.documents[f.document_id].extracted_facts_count += 1
            self.documents[f.document_id].facts.append(f)

        # Add golden verdicts from benchmark
        for v_data in data.get("verdicts", []):
            self.verdicts.append(ReconciliationVerdict(**v_data))

        self.save_to_disk()
        return True

    def ingest_facts(self, doc_summary: DocumentSummary, new_facts: List[FactAtom]):
        """
        Incrementally adds newly extracted facts from an uploaded document.
        Marks document as custom user upload, preserves it permanently,
        and re-evaluates reconciliation graph.
        """
        doc_summary.is_benchmark = False
        doc_summary.facts = list(new_facts)
        self.custom_documents[doc_summary.document_id] = doc_summary

        for f in new_facts:
            self.custom_facts[f.id] = f

        self._save_custom_uploads()

    def delete_custom_document(self, doc_id: str) -> bool:
        """
        Deletes a custom document, its extracted facts, its persisted file,
        and clears custom reconciliation verdicts.
        """
        if doc_id not in self.custom_documents:
            return False

        # 1. Remove from documents map
        del self.custom_documents[doc_id]

        # 2. Remove associated facts
        fact_ids_to_del = [fid for fid, f in self.custom_facts.items() if f.document_id == doc_id]
        for fid in fact_ids_to_del:
            del self.custom_facts[fid]

        # 3. Clear custom verdicts so rerunning knows state has changed
        self.custom_verdicts.clear()

        # 4. Remove physical file from UPLOADS_DIR if present
        target_file = UPLOADS_DIR / doc_id
        if target_file.exists():
            try:
                target_file.unlink()
            except Exception as e:
                print(f"[KnowledgeStore] Error deleting file {target_file}: {e}")

        # 5. Persist to custom_uploads.json
        self._save_custom_uploads()
        return True

    def clear_all_custom_documents(self) -> int:
        """
        Deletes all custom documents, facts, uploaded files, and verdicts.
        """
        count = len(self.custom_documents)
        doc_ids = list(self.custom_documents.keys())
        for doc_id in doc_ids:
            self.delete_custom_document(doc_id)

        self.custom_documents.clear()
        self.custom_facts.clear()
        self.custom_verdicts.clear()
        self._save_custom_uploads()
        return count

    def get_state(self) -> KnowledgeLayerState:
        verdict_counts = {
            VerdictType.CORROBORATED.value: sum(1 for v in self.verdicts if v.verdict_type == VerdictType.CORROBORATED),
            VerdictType.GENUINE_CONTRADICTION.value: sum(1 for v in self.verdicts if v.verdict_type == VerdictType.GENUINE_CONTRADICTION),
            VerdictType.APPARENT_CONTRADICTION.value: sum(1 for v in self.verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION),
            VerdictType.EXTRACTION_FAILURE.value: sum(1 for v in self.verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE),
        }

        return KnowledgeLayerState(
            documents=list(self.documents.values()),
            total_facts=len(self.facts),
            total_verdicts=len(self.verdicts),
            verdict_counts=verdict_counts,
            verdicts=self.verdicts,
            all_facts=list(self.facts.values()),
            active_benchmark=getattr(self, "active_benchmark", "delhivery"),
            custom_documents_count=len(self.custom_documents),
            custom_facts_count=len(self.custom_facts)
        )

    def reconcile_custom_uploads(self) -> List[ReconciliationVerdict]:
        """Runs the 4-case dialectic reconciliation over custom uploaded documents."""
        facts = list(self.custom_facts.values())
        docs = list(self.custom_documents.values())
        self.custom_verdicts = self.reconciler.reconcile_custom_facts(facts, docs)
        return self.custom_verdicts

    def get_custom_state(self) -> KnowledgeLayerState:
        custom_docs_list = list(self.custom_documents.values())
        custom_facts_list = list(self.custom_facts.values())

        if not self.custom_verdicts and custom_facts_list:
            self.reconcile_custom_uploads()

        verdicts = self.custom_verdicts
        verdict_counts = {
            VerdictType.CORROBORATED.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.CORROBORATED),
            VerdictType.GENUINE_CONTRADICTION.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.GENUINE_CONTRADICTION),
            VerdictType.APPARENT_CONTRADICTION.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION),
            VerdictType.EXTRACTION_FAILURE.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE),
        }

        return KnowledgeLayerState(
            documents=custom_docs_list,
            total_facts=len(custom_facts_list),
            total_verdicts=len(verdicts),
            verdict_counts=verdict_counts,
            verdicts=verdicts,
            all_facts=custom_facts_list,
            active_benchmark="custom",
            custom_documents_count=len(custom_docs_list),
            custom_facts_count=len(custom_facts_list)
        )

    def get_section_state(self, section: str) -> Dict:
        """
        Retrieves the isolated state for a specific section:
        'delhivery', 'india-macroeconomy', or 'custom'.
        """
        sec = section.lower()
        if "delhi" in sec:
            if getattr(self, "active_benchmark", "") != "delhivery" or not self.verdicts:
                self.load_benchmark("delhivery")
            verdicts = self.verdicts
            docs = list(self.documents.values())
            facts = list(self.facts.values())
        elif "macro" in sec or "india" in sec:
            if getattr(self, "active_benchmark", "") != "india-macroeconomy" or not self.verdicts:
                self.load_benchmark("india-macroeconomy")
            verdicts = self.verdicts
            docs = list(self.documents.values())
            facts = list(self.facts.values())
        else: # custom
            if not self.custom_documents:
                return {
                    "section": "custom",
                    "documents": [],
                    "total_documents": 0,
                    "total_facts": 0,
                    "total_verdicts": 0,
                    "verdict_counts": {
                        VerdictType.CORROBORATED.value: 0,
                        VerdictType.GENUINE_CONTRADICTION.value: 0,
                        VerdictType.APPARENT_CONTRADICTION.value: 0,
                        VerdictType.EXTRACTION_FAILURE.value: 0,
                    },
                    "verdicts": [],
                    "facts": [],
                    "error": "File is missing. Please upload at least one PDF to run comparison."
                }
            if not self.custom_verdicts:
                self.reconcile_custom_uploads()
            verdicts = self.custom_verdicts
            docs = list(self.custom_documents.values())
            facts = list(self.custom_facts.values())

        verdict_counts = {
            VerdictType.CORROBORATED.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.CORROBORATED),
            VerdictType.GENUINE_CONTRADICTION.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.GENUINE_CONTRADICTION),
            VerdictType.APPARENT_CONTRADICTION.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION),
            VerdictType.EXTRACTION_FAILURE.value: sum(1 for v in verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE),
        }

        return {
            "section": sec,
            "documents": [d.model_dump() for d in docs],
            "total_documents": len(docs),
            "total_facts": len(facts),
            "total_verdicts": len(verdicts),
            "verdict_counts": verdict_counts,
            "verdicts": [v.model_dump() for v in verdicts],
            "facts": [f.model_dump() for f in facts]
        }
