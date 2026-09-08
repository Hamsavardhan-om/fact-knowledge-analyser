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
from backend.config import STORAGE_FILE, BENCHMARKS_DIR


class KnowledgeStore:
    def __init__(self):
        self.documents: Dict[str, DocumentSummary] = {}
        self.facts: Dict[str, FactAtom] = {}
        self.verdicts: List[ReconciliationVerdict] = []
        self.aligner = DiscourseAligner()
        self.reconciler = DialecticReconciler()
        self._load_from_disk()

    def _load_from_disk(self):
        if STORAGE_FILE.exists():
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for doc in data.get("documents", []):
                        self.documents[doc["document_id"]] = DocumentSummary(**doc)
                    for fact in data.get("all_facts", []):
                        self.facts[fact["id"]] = FactAtom(**fact)
                    for v in data.get("verdicts", []):
                        self.verdicts.append(ReconciliationVerdict(**v))
            except Exception as e:
                print(f"[KnowledgeStore] Error loading storage.json: {e}")

    def save_to_disk(self):
        state = self.get_state()
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(), f, indent=2)

    def load_benchmark(self, dataset_name: str) -> bool:
        """
        Loads precomputed golden benchmarks (delhivery or india-macroeconomy).
        """
        filename = "delhivery_benchmark.json" if "delhi" in dataset_name.lower() else "macro_benchmark.json"
        bench_file = BENCHMARKS_DIR / filename
        if not bench_file.exists():
            return False

        with open(bench_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.facts.clear()
        self.verdicts.clear()
        self.documents.clear()

        for f_data in data.get("facts", []):
            f = FactAtom(**f_data)
            self.facts[f.id] = f
            if f.document_id not in self.documents:
                self.documents[f.document_id] = DocumentSummary(
                    document_id=f.document_id,
                    total_pages=100,
                    extracted_facts_count=0,
                    file_size_bytes=1024 * 1024,
                    upload_timestamp=datetime.now().isoformat()
                )
            self.documents[f.document_id].extracted_facts_count += 1

        for v_data in data.get("verdicts", []):
            self.verdicts.append(ReconciliationVerdict(**v_data))

        self.save_to_disk()
        return True

    def ingest_facts(self, doc_summary: DocumentSummary, new_facts: List[FactAtom]):
        """
        Incrementally adds newly extracted facts from an uploaded document.
        Re-evaluates clusters and updates reconciliation verdicts.
        """
        self.documents[doc_summary.document_id] = doc_summary
        for f in new_facts:
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
