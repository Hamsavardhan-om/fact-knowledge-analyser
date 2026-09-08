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
        from backend.core.extractor import FactExtractor

        if not UPLOADS_DIR.exists():
            return

        for pdf_path in UPLOADS_DIR.glob("*.pdf"):
            if "delhivery" in pdf_path.name.lower() or "macro" in pdf_path.name.lower():
                continue
            if pdf_path.name in self.custom_documents:
                continue
            try:
                pages = DocumentPerception.parse_pdf(pdf_path)
                facts = []
                for p in pages:
                    p_facts = FactExtractor.extract_facts_from_page(
                        page_text=p["text"],
                        page_number=p["page_number"],
                        document_id=pdf_path.name,
                        tables=p.get("tables", [])
                    )
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
                self.documents[doc_summary.document_id] = doc_summary
                for f in facts:
                    self.custom_facts[f.id] = f
                    self.facts[f.id] = f
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
                    for doc in data.get("documents", []):
                        d = DocumentSummary(**doc)
                        self.documents[d.document_id] = d
                        if not d.is_benchmark:
                            self.custom_documents[d.document_id] = d
                    for fact in data.get("all_facts", []):
                        fa = FactAtom(**fact)
                        self.facts[fa.id] = fa
                        if fa.document_id in self.custom_documents:
                            self.custom_facts[fa.id] = fa
                    for v in data.get("verdicts", []):
                        self.verdicts.append(ReconciliationVerdict(**v))
            except Exception as e:
                print(f"[KnowledgeStore] Error loading storage.json: {e}")

        # Ensure custom uploads are merged into store
        for doc_id, doc in self.custom_documents.items():
            self.documents[doc_id] = doc
        for f_id, fact in self.custom_facts.items():
            self.facts[f_id] = fact

    def save_to_disk(self):
        state = self.get_state()
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2)
        self._save_custom_uploads()

    def load_benchmark(self, dataset_name: str) -> bool:
        """
        Loads precomputed golden benchmarks (delhivery or india-macroeconomy).
        Crucially PRESERVES any user-uploaded custom PDFs and facts!
        """
        filename = "delhivery_benchmark.json" if "delhi" in dataset_name.lower() else "macro_benchmark.json"
        bench_file = BENCHMARKS_DIR / filename
        if not bench_file.exists():
            return False

        with open(bench_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Reset state to ONLY custom user-uploaded documents and facts
        self.documents = dict(self.custom_documents)
        self.facts = dict(self.custom_facts)
        self.verdicts.clear()

        # 2. Add the benchmark facts and documents
        for f_data in data.get("facts", []):
            f = FactAtom(**f_data)
            self.facts[f.id] = f
            if f.document_id not in self.documents:
                self.documents[f.document_id] = DocumentSummary(
                    document_id=f.document_id,
                    total_pages=100,
                    extracted_facts_count=0,
                    file_size_bytes=1024 * 1024,
                    upload_timestamp=datetime.now().isoformat(),
                    is_benchmark=True,
                    benchmark_name=dataset_name
                )
            self.documents[f.document_id].extracted_facts_count += 1

        # 3. Add golden verdicts from benchmark
        for v_data in data.get("verdicts", []):
            self.verdicts.append(ReconciliationVerdict(**v_data))

        # 4. If custom facts exist, cluster all facts and reconcile
        if self.custom_facts:
            all_clusters = self.aligner.cluster_facts(list(self.facts.values()))
            custom_verdicts = self.reconciler.reconcile_all_clusters(all_clusters)
            existing_ids = {v.id for v in self.verdicts}
            for cv in custom_verdicts:
                if cv.id not in existing_ids:
                    # Include if it touches custom facts
                    if any(cf.document_id in self.custom_documents for cf in cv.facts):
                        self.verdicts.append(cv)

        self.save_to_disk()
        return True

    def ingest_facts(self, doc_summary: DocumentSummary, new_facts: List[FactAtom]):
        """
        Incrementally adds newly extracted facts from an uploaded document.
        Marks document as custom user upload, preserves it permanently,
        and re-evaluates reconciliation graph.
        """
        doc_summary.is_benchmark = False
        self.custom_documents[doc_summary.document_id] = doc_summary
        self.documents[doc_summary.document_id] = doc_summary

        for f in new_facts:
            self.custom_facts[f.id] = f
            self.facts[f.id] = f

        # Cluster all facts
        clusters = self.aligner.cluster_facts(list(self.facts.values()))

        # Reconcile multi-document clusters
        new_verdicts = self.reconciler.reconcile_all_clusters(clusters)
        self.verdicts = new_verdicts

        self.save_to_disk()

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
            all_facts=list(self.facts.values())
        )
