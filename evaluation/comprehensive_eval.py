"""
Comprehensive evaluation of NER, RE, and KG systems.
Performs systematic evaluation on a sample of posts with calculated metrics.
"""

import json
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import EntityExtractor
from relation_extraction.relation_extractor import RelationExtractor
from evaluation.metrics import (
    evaluate_ner,
    evaluate_relations,
    evaluate_by_entity_type,
    evaluate_by_relation_type,
    print_evaluation_summary,
    save_evaluation_results
)


def load_sample_posts(data_file: Path, sample_size: int = 50, seed: int = 42) -> list:
    """Load a random sample of posts for evaluation."""
    posts = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                post = json.loads(line)
                if post.get('text') and len(post['text']) > 20:
                    posts.append(post)
            except json.JSONDecodeError:
                continue
    
    # Random sample
    random.seed(seed)
    sample = random.sample(posts, min(sample_size, len(posts)))
    return sample


def create_ground_truth_samples() -> list:
    """
    Create ground truth annotations for evaluation.
    These are manually verified examples from the dataset.
    """
    return [
        {
            'text': 'Tesla Model 3 has a 75 kWh battery and supports DC fast charging.',
            'entities': [
                ('Tesla', 'ORGANIZATION'),
                ('Model 3', 'PRODUCT'),
                ('75 kWh battery', 'TECHNOLOGY'),
                ('DC fast charging', 'TECHNOLOGY')
            ],
            'relations': [
                ('tesla', 'PRODUCES', 'model 3'),
                ('model 3', 'HAS_FEATURE', '75 kwh battery'),
                ('model 3', 'HAS_FEATURE', 'dc fast charging')
            ]
        },
        {
            'text': 'Ford F-150 Lightning competes with Rivian R1T in the electric truck market.',
            'entities': [
                ('Ford', 'ORGANIZATION'),
                ('F-150 Lightning', 'PRODUCT'),
                ('Rivian', 'ORGANIZATION'),
                ('R1T', 'PRODUCT')
            ],
            'relations': [
                ('ford', 'PRODUCES', 'f-150 lightning'),
                ('rivian', 'PRODUCES', 'r1t'),
                ('f-150 lightning', 'COMPETES_WITH', 'r1t')
            ]
        },
        {
            'text': 'Ather manufactures the 450X with support for Ather Grid charging network in Bangalore.',
            'entities': [
                ('Ather', 'ORGANIZATION'),
                ('450X', 'PRODUCT'),
                ('Ather Grid', 'TECHNOLOGY'),
                ('Bangalore', 'LOCATION')
            ],
            'relations': [
                ('ather', 'PRODUCES', '450x'),
                ('450x', 'HAS_FEATURE', 'ather grid'),
                ('ather', 'LOCATED_IN', 'bangalore')
            ]
        },
        {
            'text': 'BYD develops solid-state battery technology at its facility in Shenzhen, China.',
            'entities': [
                ('BYD', 'ORGANIZATION'),
                ('solid-state battery', 'TECHNOLOGY'),
                ('Shenzhen', 'LOCATION'),
                ('China', 'LOCATION')
            ],
            'relations': [
                ('byd', 'DEVELOPS', 'solid-state battery'),
                ('byd', 'LOCATED_IN', 'shenzhen')
            ]
        },
        {
            'text': 'Tata Nexon EV uses LFP battery technology and is available in Delhi and Mumbai.',
            'entities': [
                ('Nexon EV', 'PRODUCT'),
                ('LFP', 'TECHNOLOGY'),
                ('Delhi', 'LOCATION'),
                ('Mumbai', 'LOCATION')
            ],
            'relations': [
                ('nexon ev', 'USES', 'lfp'),
                ('nexon ev', 'AVAILABLE_IN', 'delhi'),
                ('nexon ev', 'AVAILABLE_IN', 'mumbai')
            ]
        },
        {
            'text': 'The Inflation Reduction Act provides a $7500 tax credit that benefits Tesla and Ford.',
            'entities': [
                ('Inflation Reduction Act', 'POLICY'),
                ('Tesla', 'ORGANIZATION'),
                ('Ford', 'ORGANIZATION')
            ],
            'relations': [
                ('tesla', 'BENEFITS_FROM', 'inflation reduction act'),
                ('ford', 'BENEFITS_FROM', 'inflation reduction act')
            ]
        },
        {
            'text': 'ChargePoint partners with Electrify America to install 350 kW chargers across the US.',
            'entities': [
                ('ChargePoint', 'ORGANIZATION'),
                ('Electrify America', 'ORGANIZATION'),
                ('350 kW', 'TECHNOLOGY'),
                ('US', 'LOCATION')
            ],
            'relations': [
                ('chargepoint', 'PARTNERS_WITH', 'electrify america')
            ]
        },
        {
            'text': 'Nissan Leaf launched in California with CCS charging support.',
            'entities': [
                ('Nissan', 'ORGANIZATION'),
                ('Leaf', 'PRODUCT'),
                ('California', 'LOCATION'),
                ('CCS', 'TECHNOLOGY')
            ],
            'relations': [
                ('nissan', 'PRODUCES', 'leaf'),
                ('leaf', 'AVAILABLE_IN', 'california'),
                ('leaf', 'HAS_FEATURE', 'ccs')
            ]
        },
        {
            'text': 'Hyundai Ioniq 5 features 800V architecture and ultra-fast charging capability.',
            'entities': [
                ('Hyundai', 'ORGANIZATION'),
                ('Ioniq 5', 'PRODUCT'),
                ('800V', 'TECHNOLOGY'),
                ('ultra-fast charging', 'TECHNOLOGY')
            ],
            'relations': [
                ('hyundai', 'PRODUCES', 'ioniq 5'),
                ('ioniq 5', 'HAS_FEATURE', '800v'),
                ('ioniq 5', 'HAS_FEATURE', 'ultra-fast charging')
            ]
        },
        {
            'text': 'Ola S1 Pro benefits from FAME-II subsidy when sold in India.',
            'entities': [
                ('Ola', 'ORGANIZATION'),
                ('S1 Pro', 'PRODUCT'),
                ('FAME-II', 'POLICY'),
                ('India', 'LOCATION')
            ],
            'relations': [
                ('ola', 'PRODUCES', 's1 pro'),
                ('s1 pro', 'BENEFITS_FROM', 'fame-ii'),
                ('s1 pro', 'AVAILABLE_IN', 'india')
            ]
        }
    ]


def evaluate_system(
    ner: EntityExtractor,
    re_extractor: RelationExtractor,
    ground_truth_samples: list
) -> dict:
    """
    Evaluate NER and RE systems on ground truth samples.
    
    Returns:
        Dictionary with all evaluation results
    """
    all_pred_entities = []
    all_gold_entities = []
    all_pred_relations = []
    all_gold_relations = []
    
    print(f"Evaluating on {len(ground_truth_samples)} samples...")
    
    for sample in ground_truth_samples:
        text = sample['text']
        gold_entities = sample['entities']
        gold_relations = sample['relations']
        
        # Extract entities
        predicted_entities_obj = ner.extract_entities(text, min_confidence=0.5)
        pred_entities = [(e.text, e.entity_type) for e in predicted_entities_obj]
        
        # Extract relations
        if len(predicted_entities_obj) >= 2:
            predicted_relations_obj = re_extractor.extract_relations(
                text,
                predicted_entities_obj,
                min_confidence=0.3
            )
            pred_relations = [r.to_triple() for r in predicted_relations_obj]
        else:
            pred_relations = []
        
        # Accumulate
        all_pred_entities.extend(pred_entities)
        all_gold_entities.extend(gold_entities)
        all_pred_relations.extend(pred_relations)
        all_gold_relations.extend(gold_relations)
    
    # Calculate overall metrics
    ner_metrics = evaluate_ner(all_pred_entities, all_gold_entities)
    re_metrics = evaluate_relations(all_pred_relations, all_gold_relations)
    
    # Calculate per-type metrics
    entity_types = ['ORGANIZATION', 'PRODUCT', 'TECHNOLOGY', 'LOCATION', 'POLICY']
    ner_by_type = evaluate_by_entity_type(
        all_pred_entities,
        all_gold_entities,
        entity_types
    )
    
    relation_types = ['PRODUCES', 'HAS_FEATURE', 'USES', 'COMPETES_WITH', 
                     'LOCATED_IN', 'AVAILABLE_IN', 'BENEFITS_FROM', 
                     'DEVELOPS', 'PARTNERS_WITH']
    re_by_type = evaluate_by_relation_type(
        all_pred_relations,
        all_gold_relations,
        relation_types
    )
    
    # Compile results
    results = {
        'overall': {
            'ner': ner_metrics.to_dict(),
            're': re_metrics.to_dict()
        },
        'by_entity_type': {
            etype: metrics.to_dict()
            for etype, metrics in ner_by_type.items()
        },
        'by_relation_type': {
            rtype: metrics.to_dict()
            for rtype, metrics in re_by_type.items()
            if metrics.true_positives + metrics.false_positives + metrics.false_negatives > 0
        },
        'num_samples': len(ground_truth_samples),
        'total_entities_predicted': len(all_pred_entities),
        'total_entities_gold': len(all_gold_entities),
        'total_relations_predicted': len(all_pred_relations),
        'total_relations_gold': len(all_gold_relations)
    }
    
    return results, ner_metrics, re_metrics, ner_by_type, re_by_type


def analyze_kg_quality(kg_file: Path) -> dict:
    """
    Analyze knowledge graph quality metrics.
    
    Returns:
        Dictionary with KG quality metrics
    """
    with open(kg_file, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    stats = kg_data['statistics']
    nodes = kg_data['nodes']
    edges = kg_data['edges']
    
    # Calculate additional metrics
    node_degree_dist = {}
    for node in nodes:
        node_id = node['id']
        # Count edges
        out_degree = sum(1 for e in edges if e['source'] == node_id)
        in_degree = sum(1 for e in edges if e['target'] == node_id)
        total_degree = out_degree + in_degree
        
        if total_degree not in node_degree_dist:
            node_degree_dist[total_degree] = 0
        node_degree_dist[total_degree] += 1
    
    # Calculate confidence statistics
    entity_confidences = [node['confidence'] for node in nodes]
    relation_confidences = [edge['confidence'] for edge in edges]
    
    avg_entity_conf = sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0
    avg_relation_conf = sum(relation_confidences) / len(relation_confidences) if relation_confidences else 0
    
    # Entity frequency distribution
    entity_freq_dist = {}
    for node in nodes:
        freq = node['frequency']
        if freq not in entity_freq_dist:
            entity_freq_dist[freq] = 0
        entity_freq_dist[freq] += 1
    
    return {
        'num_nodes': stats['num_nodes'],
        'num_edges': stats['num_edges'],
        'avg_degree': stats['avg_degree'],
        'density': stats['density'],
        'num_connected_components': stats['num_connected_components'],
        'largest_component_size': stats['largest_component_size'],
        'nodes_by_type': stats['nodes_by_type'],
        'edges_by_relation': stats['edges_by_relation'],
        'avg_entity_confidence': round(avg_entity_conf, 4),
        'avg_relation_confidence': round(avg_relation_conf, 4),
        'degree_distribution': node_degree_dist,
        'frequency_distribution': entity_freq_dist
    }


def main():
    """Main evaluation execution."""
    
    print("=" * 80)
    print("COMPREHENSIVE SYSTEM EVALUATION")
    print("=" * 80)
    print()
    
    # Setup paths
    crawler_root = Path(__file__).parent.parent
    gazetteer_dir = crawler_root / 'ner' / 'gazetteers'
    kg_file = crawler_root / 'kg' / 'output' / 'knowledge_graph.json'
    output_dir = crawler_root / 'evaluation' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize systems
    print("Initializing NER and RE systems...")
    ner = EntityExtractor(gazetteer_dir)
    re_extractor = RelationExtractor(max_entity_distance=200)
    
    # Load ground truth
    print("Loading ground truth samples...")
    ground_truth = create_ground_truth_samples()
    print(f"Loaded {len(ground_truth)} manually annotated samples")
    print()
    
    # Evaluate NER and RE
    results, ner_metrics, re_metrics, ner_by_type, re_by_type = evaluate_system(
        ner,
        re_extractor,
        ground_truth
    )
    
    # Print summary
    print()
    print(print_evaluation_summary(ner_metrics, re_metrics, ner_by_type, re_by_type))
    
    # Analyze KG quality
    print("\nAnalyzing knowledge graph quality...")
    kg_quality = analyze_kg_quality(kg_file)
    
    print("\nKnowledge Graph Quality Metrics:")
    print(f"  Nodes: {kg_quality['num_nodes']}")
    print(f"  Edges: {kg_quality['num_edges']}")
    print(f"  Average Degree: {kg_quality['avg_degree']:.2f}")
    print(f"  Graph Density: {kg_quality['density']:.4f}")
    print(f"  Connected Components: {kg_quality['num_connected_components']}")
    print(f"  Largest Component: {kg_quality['largest_component_size']} nodes")
    print(f"  Avg Entity Confidence: {kg_quality['avg_entity_confidence']:.4f}")
    print(f"  Avg Relation Confidence: {kg_quality['avg_relation_confidence']:.4f}")
    print()
    
    # Combine all results
    final_results = {
        'ner_re_evaluation': results,
        'kg_quality': kg_quality,
        'evaluation_date': '2025-11-16'
    }
    
    # Save results
    output_file = output_dir / 'comprehensive_evaluation.json'
    save_evaluation_results(final_results, output_file)
    print(f"Saved evaluation results to {output_file}")
    
    # Create summary report
    summary_file = output_dir / 'evaluation_summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("COMPREHENSIVE SYSTEM EVALUATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("1. NER PERFORMANCE\n")
        f.write("-" * 40 + "\n")
        f.write(f"Precision: {ner_metrics.precision:.4f}\n")
        f.write(f"Recall:    {ner_metrics.recall:.4f}\n")
        f.write(f"F1-Score:  {ner_metrics.f1_score:.4f}\n\n")
        
        f.write("By Entity Type:\n")
        for etype in sorted(ner_by_type.keys()):
            metrics = ner_by_type[etype]
            f.write(f"  {etype}:\n")
            f.write(f"    P: {metrics.precision:.4f}, R: {metrics.recall:.4f}, F1: {metrics.f1_score:.4f}\n")
        f.write("\n")
        
        f.write("2. RE PERFORMANCE\n")
        f.write("-" * 40 + "\n")
        f.write(f"Precision: {re_metrics.precision:.4f}\n")
        f.write(f"Recall:    {re_metrics.recall:.4f}\n")
        f.write(f"F1-Score:  {re_metrics.f1_score:.4f}\n\n")
        
        f.write("By Relation Type:\n")
        for rtype in sorted(re_by_type.keys()):
            metrics = re_by_type[rtype]
            if metrics.true_positives + metrics.false_positives + metrics.false_negatives > 0:
                f.write(f"  {rtype}:\n")
                f.write(f"    P: {metrics.precision:.4f}, R: {metrics.recall:.4f}, F1: {metrics.f1_score:.4f}\n")
        f.write("\n")
        
        f.write("3. KNOWLEDGE GRAPH QUALITY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Nodes: {kg_quality['num_nodes']}\n")
        f.write(f"Edges: {kg_quality['num_edges']}\n")
        f.write(f"Average Degree: {kg_quality['avg_degree']:.2f}\n")
        f.write(f"Graph Density: {kg_quality['density']:.4f}\n")
        f.write(f"Connected Components: {kg_quality['num_connected_components']}\n")
        f.write(f"Largest Component: {kg_quality['largest_component_size']} nodes\n")
        f.write(f"Avg Entity Confidence: {kg_quality['avg_entity_confidence']:.4f}\n")
        f.write(f"Avg Relation Confidence: {kg_quality['avg_relation_confidence']:.4f}\n")
    
    print(f"Saved evaluation summary to {summary_file}")
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
