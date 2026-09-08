"""
Discourse Topic Aligner & Semantic Canonicalizer.
Groups FactAtoms into shared discourse topics across independent documents
without rigid hardcoded taxonomies.
"""

import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from backend.models.schemas import FactAtom


class DiscourseAligner:
    """
    Groups facts across documents into coherent discourse topics based on
    Entity and Attribute semantic affinity.
    """

    def __init__(self, similarity_threshold: float = 0.65):
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower()
        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)
        # Remove stop words
        stopwords = {"of", "the", "in", "at", "for", "from", "to", "and", "a", "an", "limited", "ltd"}
        tokens = [w for w in text.split() if w not in stopwords]
        return " ".join(tokens)

    @classmethod
    def _token_jaccard_similarity(cls, s1: str, s2: str) -> float:
        set1 = set(cls._normalize_text(s1).split())
        set2 = set(cls._normalize_text(s2).split())
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    @classmethod
    def _compute_affinity(cls, f1: FactAtom, f2: FactAtom) -> float:
        # Check entity compatibility
        norm_e1 = cls._normalize_text(f1.entity)
        norm_e2 = cls._normalize_text(f2.entity)
        
        # If entities are completely unrelated, do not align
        entity_sim = cls._token_jaccard_similarity(norm_e1, norm_e2)
        if entity_sim < 0.2 and norm_e1 != norm_e2:
            return 0.0

        # Attribute similarity
        attr_sim = cls._token_jaccard_similarity(f1.attribute, f2.attribute)

        # Domain synonym heuristics
        if any(term in f1.attribute.lower() for term in ["pin code", "pincode"]) and \
           any(term in f2.attribute.lower() for term in ["pin code", "pincode"]):
            attr_sim = max(attr_sim, 0.85)

        if any(term in f1.attribute.lower() for term in ["real gdp", "economic growth"]) and \
           any(term in f2.attribute.lower() for term in ["real gdp", "economic growth", "gdp at market prices"]):
            attr_sim = max(attr_sim, 0.90)

        if any(term in f1.attribute.lower() for term in ["parcel", "shipment"]) and \
           any(term in f2.attribute.lower() for term in ["parcel", "shipment"]):
            attr_sim = max(attr_sim, 0.85)

        if any(term in f1.attribute.lower() for term in ["inflation", "cpi"]) and \
           any(term in f2.attribute.lower() for term in ["inflation", "cpi"]):
            attr_sim = max(attr_sim, 0.85)

        return (0.3 * entity_sim) + (0.7 * attr_sim)

    def cluster_facts(self, facts: List[FactAtom]) -> Dict[str, List[FactAtom]]:
        """
        Groups facts into discourse clusters.
        Returns a dict mapping canonical_topic_name -> list of FactAtoms.
        """
        clusters: Dict[str, List[FactAtom]] = defaultdict(list)
        cluster_representatives: Dict[str, FactAtom] = {}

        for fact in facts:
            matched_cluster = None
            best_score = 0.0

            for topic_name, rep_fact in cluster_representatives.items():
                score = self._compute_affinity(fact, rep_fact)
                if score >= self.similarity_threshold and score > best_score:
                    best_score = score
                    matched_cluster = topic_name

            if matched_cluster:
                clusters[matched_cluster].append(fact)
            else:
                # Seed a new cluster
                new_topic = f"{fact.entity}: {fact.attribute}"
                cluster_representatives[new_topic] = fact
                clusters[new_topic].append(fact)

        return dict(clusters)
