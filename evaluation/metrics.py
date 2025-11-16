"""
Evaluation metrics for NER and RE systems.
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'precision': round(self.precision, 4),
            'recall': round(self.recall, 4),
            'f1_score': round(self.f1_score, 4),
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives
        }


def calculate_metrics(
    true_positives: int,
    false_positives: int,
    false_negatives: int
) -> EvaluationMetrics:
    """
    Calculate precision, recall, and F1-score.
    
    Args:
        true_positives: Number of correct predictions
        false_positives: Number of incorrect predictions
        false_negatives: Number of missed predictions
    
    Returns:
        EvaluationMetrics object
    """
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return EvaluationMetrics(
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives
    )


def evaluate_ner(
    predicted_entities: List[Tuple[str, str]],  # (text, type)
    ground_truth_entities: List[Tuple[str, str]]
) -> EvaluationMetrics:
    """
    Evaluate NER predictions against ground truth.
    
    Args:
        predicted_entities: List of (text, type) tuples
        ground_truth_entities: List of (text, type) tuples
    
    Returns:
        EvaluationMetrics object
    """
    # Normalize entities (lowercase, strip whitespace)
    pred_set = set((text.lower().strip(), etype) for text, etype in predicted_entities)
    gold_set = set((text.lower().strip(), etype) for text, etype in ground_truth_entities)
    
    true_positives = len(pred_set & gold_set)
    false_positives = len(pred_set - gold_set)
    false_negatives = len(gold_set - pred_set)
    
    return calculate_metrics(true_positives, false_positives, false_negatives)


def evaluate_relations(
    predicted_relations: List[Tuple[str, str, str]],  # (subject, predicate, object)
    ground_truth_relations: List[Tuple[str, str, str]]
) -> EvaluationMetrics:
    """
    Evaluate relation extraction predictions against ground truth.
    
    Args:
        predicted_relations: List of (subject, predicate, object) triples
        ground_truth_relations: List of (subject, predicate, object) triples
    
    Returns:
        EvaluationMetrics object
    """
    # Normalize triples
    pred_set = set(
        (subj.lower().strip(), pred, obj.lower().strip())
        for subj, pred, obj in predicted_relations
    )
    gold_set = set(
        (subj.lower().strip(), pred, obj.lower().strip())
        for subj, pred, obj in ground_truth_relations
    )
    
    true_positives = len(pred_set & gold_set)
    false_positives = len(pred_set - gold_set)
    false_negatives = len(gold_set - pred_set)
    
    return calculate_metrics(true_positives, false_positives, false_negatives)


def evaluate_by_entity_type(
    predicted_entities: List[Tuple[str, str]],
    ground_truth_entities: List[Tuple[str, str]],
    entity_types: List[str]
) -> Dict[str, EvaluationMetrics]:
    """
    Evaluate NER performance for each entity type separately.
    
    Args:
        predicted_entities: List of (text, type) tuples
        ground_truth_entities: List of (text, type) tuples
        entity_types: List of entity types to evaluate
    
    Returns:
        Dictionary mapping entity type to EvaluationMetrics
    """
    results = {}
    
    for etype in entity_types:
        # Filter by entity type
        pred_filtered = [(text, t) for text, t in predicted_entities if t == etype]
        gold_filtered = [(text, t) for text, t in ground_truth_entities if t == etype]
        
        # Calculate metrics
        metrics = evaluate_ner(pred_filtered, gold_filtered)
        results[etype] = metrics
    
    return results


def evaluate_by_relation_type(
    predicted_relations: List[Tuple[str, str, str]],
    ground_truth_relations: List[Tuple[str, str, str]],
    relation_types: List[str]
) -> Dict[str, EvaluationMetrics]:
    """
    Evaluate RE performance for each relation type separately.
    
    Args:
        predicted_relations: List of (subject, predicate, object) triples
        ground_truth_relations: List of (subject, predicate, object) triples
        relation_types: List of relation types to evaluate
    
    Returns:
        Dictionary mapping relation type to EvaluationMetrics
    """
    results = {}
    
    for rtype in relation_types:
        # Filter by relation type
        pred_filtered = [(s, p, o) for s, p, o in predicted_relations if p == rtype]
        gold_filtered = [(s, p, o) for s, p, o in ground_truth_relations if p == rtype]
        
        # Calculate metrics
        metrics = evaluate_relations(pred_filtered, gold_filtered)
        results[rtype] = metrics
    
    return results


def load_annotations(annotation_file: Path) -> Dict:
    """
    Load manual annotations from JSON file.
    
    Args:
        annotation_file: Path to annotation file
    
    Returns:
        Dictionary with annotations
    """
    with open(annotation_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_evaluation_results(results: Dict, output_file: Path) -> None:
    """
    Save evaluation results to JSON file.
    
    Args:
        results: Dictionary with evaluation results
        output_file: Path to output file
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def print_evaluation_summary(
    ner_metrics: EvaluationMetrics,
    re_metrics: EvaluationMetrics,
    ner_by_type: Dict[str, EvaluationMetrics] = None,
    re_by_type: Dict[str, EvaluationMetrics] = None
) -> str:
    """
    Create a formatted string summary of evaluation results.
    
    Args:
        ner_metrics: Overall NER metrics
        re_metrics: Overall RE metrics
        ner_by_type: NER metrics by entity type (optional)
        re_by_type: RE metrics by relation type (optional)
    
    Returns:
        Formatted string
    """
    lines = []
    lines.append("=" * 70)
    lines.append("EVALUATION RESULTS")
    lines.append("=" * 70)
    lines.append("")
    
    # Overall NER metrics
    lines.append("Named Entity Recognition (Overall):")
    lines.append(f"  Precision: {ner_metrics.precision:.4f}")
    lines.append(f"  Recall:    {ner_metrics.recall:.4f}")
    lines.append(f"  F1-Score:  {ner_metrics.f1_score:.4f}")
    lines.append(f"  TP: {ner_metrics.true_positives}, FP: {ner_metrics.false_positives}, FN: {ner_metrics.false_negatives}")
    lines.append("")
    
    # NER by entity type
    if ner_by_type:
        lines.append("NER by Entity Type:")
        for etype, metrics in sorted(ner_by_type.items()):
            lines.append(f"  {etype}:")
            lines.append(f"    P: {metrics.precision:.4f}, R: {metrics.recall:.4f}, F1: {metrics.f1_score:.4f}")
        lines.append("")
    
    # Overall RE metrics
    lines.append("Relation Extraction (Overall):")
    lines.append(f"  Precision: {re_metrics.precision:.4f}")
    lines.append(f"  Recall:    {re_metrics.recall:.4f}")
    lines.append(f"  F1-Score:  {re_metrics.f1_score:.4f}")
    lines.append(f"  TP: {re_metrics.true_positives}, FP: {re_metrics.false_positives}, FN: {re_metrics.false_negatives}")
    lines.append("")
    
    # RE by relation type
    if re_by_type:
        lines.append("RE by Relation Type:")
        for rtype, metrics in sorted(re_by_type.items()):
            if metrics.true_positives + metrics.false_positives + metrics.false_negatives > 0:
                lines.append(f"  {rtype}:")
                lines.append(f"    P: {metrics.precision:.4f}, R: {metrics.recall:.4f}, F1: {metrics.f1_score:.4f}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return '\n'.join(lines)
