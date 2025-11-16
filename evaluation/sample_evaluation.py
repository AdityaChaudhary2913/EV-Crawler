"""
Sample evaluation script demonstrating metrics calculation.
Creates synthetic ground truth for demonstration.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.metrics import (
    evaluate_ner,
    evaluate_relations,
    evaluate_by_entity_type,
    evaluate_by_relation_type,
    print_evaluation_summary
)


def create_sample_annotations():
    """Create sample ground truth annotations for testing."""
    
    # Sample predictions from our system
    predicted_entities = [
        ("Tesla", "ORGANIZATION"),
        ("Model 3", "PRODUCT"),
        ("75 kWh battery", "TECHNOLOGY"),
        ("DC fast charging", "TECHNOLOGY"),
        ("CCS2", "TECHNOLOGY"),
        ("Ford", "ORGANIZATION"),
        ("F-150 Lightning", "PRODUCT"),
        ("Rivian", "ORGANIZATION"),
        ("R1T", "PRODUCT"),
        ("Bangalore", "LOCATION"),
        ("Ather", "ORGANIZATION"),
        ("450X", "PRODUCT"),
        ("US", "LOCATION"),
        ("FAME-II", "POLICY"),
    ]
    
    # Ground truth (assume our system is mostly correct with a few errors/misses)
    ground_truth_entities = [
        ("Tesla", "ORGANIZATION"),
        ("Model 3", "PRODUCT"),
        ("75 kWh battery", "TECHNOLOGY"),
        ("DC fast charging", "TECHNOLOGY"),
        ("CCS2", "TECHNOLOGY"),
        ("Ford", "ORGANIZATION"),
        ("F-150 Lightning", "PRODUCT"),
        ("Rivian", "ORGANIZATION"),
        ("R1T", "PRODUCT"),
        ("Bangalore", "LOCATION"),
        ("Ather", "ORGANIZATION"),
        ("450X", "PRODUCT"),
        ("United States", "LOCATION"),  # Our system predicted "US" instead
        ("FAME-II", "POLICY"),
        ("Elon Musk", "PERSON"),  # Our system missed this
    ]
    
    # Sample relation predictions
    predicted_relations = [
        ("Tesla", "PRODUCES", "Model 3"),
        ("Model 3", "HAS_FEATURE", "75 kWh battery"),
        ("Ford", "PRODUCES", "F-150 Lightning"),
        ("Rivian", "PRODUCES", "R1T"),
        ("F-150 Lightning", "COMPETES_WITH", "R1T"),
        ("Ather", "PRODUCES", "450X"),
        ("450X", "AVAILABLE_IN", "Bangalore"),
    ]
    
    # Ground truth relations
    ground_truth_relations = [
        ("Tesla", "PRODUCES", "Model 3"),
        ("Model 3", "HAS_FEATURE", "75 kWh battery"),
        ("Model 3", "HAS_FEATURE", "DC fast charging"),  # Missed by our system
        ("Ford", "PRODUCES", "F-150 Lightning"),
        ("Rivian", "PRODUCES", "R1T"),
        ("F-150 Lightning", "COMPETES_WITH", "R1T"),
        ("Ather", "PRODUCES", "450X"),
        ("450X", "AVAILABLE_IN", "Bangalore"),
    ]
    
    return predicted_entities, ground_truth_entities, predicted_relations, ground_truth_relations


def main():
    """Run sample evaluation."""
    
    print("=" * 70)
    print("SAMPLE EVALUATION DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Get sample data
    pred_entities, gold_entities, pred_relations, gold_relations = create_sample_annotations()
    
    print(f"Predicted entities: {len(pred_entities)}")
    print(f"Ground truth entities: {len(gold_entities)}")
    print(f"Predicted relations: {len(pred_relations)}")
    print(f"Ground truth relations: {len(gold_relations)}")
    print()
    
    # Evaluate NER
    ner_metrics = evaluate_ner(pred_entities, gold_entities)
    
    # Evaluate RE
    re_metrics = evaluate_relations(pred_relations, gold_relations)
    
    # Evaluate by entity type
    entity_types = ["ORGANIZATION", "PRODUCT", "LOCATION", "TECHNOLOGY", "POLICY", "PERSON"]
    ner_by_type = evaluate_by_entity_type(pred_entities, gold_entities, entity_types)
    
    # Evaluate by relation type
    relation_types = ["PRODUCES", "HAS_FEATURE", "COMPETES_WITH", "AVAILABLE_IN"]
    re_by_type = evaluate_by_relation_type(pred_relations, gold_relations, relation_types)
    
    # Print summary
    summary = print_evaluation_summary(ner_metrics, re_metrics, ner_by_type, re_by_type)
    print(summary)
    
    # Show errors
    print("\nError Analysis:")
    print("-" * 70)
    
    pred_set = set((text.lower().strip(), etype) for text, etype in pred_entities)
    gold_set = set((text.lower().strip(), etype) for text, etype in gold_entities)
    
    false_positives_ner = pred_set - gold_set
    false_negatives_ner = gold_set - pred_set
    
    if false_positives_ner:
        print("\nFalse Positives (NER - predicted but incorrect):")
        for text, etype in false_positives_ner:
            print(f"  - {text} ({etype})")
    
    if false_negatives_ner:
        print("\nFalse Negatives (NER - missed by system):")
        for text, etype in false_negatives_ner:
            print(f"  - {text} ({etype})")
    
    pred_rel_set = set(
        (s.lower().strip(), p, o.lower().strip())
        for s, p, o in pred_relations
    )
    gold_rel_set = set(
        (s.lower().strip(), p, o.lower().strip())
        for s, p, o in gold_relations
    )
    
    false_negatives_re = gold_rel_set - pred_rel_set
    
    if false_negatives_re:
        print("\nFalse Negatives (RE - missed relations):")
        for s, p, o in false_negatives_re:
            print(f"  - ({s}, {p}, {o})")
    
    print()


if __name__ == '__main__':
    main()
