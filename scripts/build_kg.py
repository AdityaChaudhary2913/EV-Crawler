"""
Main pipeline for building Knowledge Graph from dataset.
Processes posts.jsonl and extracts entities, relations, and constructs KG.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import EntityExtractor
from relation_extraction.relation_extractor import RelationExtractor
from kg.graph_builder import KnowledgeGraph, visualize_graph_statistics


def load_posts(data_file: Path, limit: Optional[int] = None) -> List[Dict]:
    """
    Load posts from JSONL file.
    
    Args:
        data_file: Path to posts.jsonl
        limit: Maximum number of posts to load (None = all)
    
    Returns:
        List of post dictionaries
    """
    posts = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            try:
                post = json.loads(line)
                posts.append(post)
            except json.JSONDecodeError:
                continue
    
    return posts


def process_posts(
    posts: List[Dict],
    ner: EntityExtractor,
    re_extractor: RelationExtractor,
    min_entity_confidence: float = 0.5,
    min_relation_confidence: float = 0.3
) -> tuple:
    """
    Process posts to extract entities and relations.
    
    Args:
        posts: List of post dictionaries
        ner: Entity extractor
        re_extractor: Relation extractor
        min_entity_confidence: Minimum entity confidence
        min_relation_confidence: Minimum relation confidence
    
    Returns:
        Tuple of (all_entities, all_relations)
    """
    all_entities = []
    all_relations = []
    
    print(f"\nProcessing {len(posts)} posts...")
    
    for post in tqdm(posts, desc="Extracting entities and relations"):
        # Get text content
        text = post.get('text', '')
        if not text or len(text) < 10:
            continue
        
        # Extract entities
        entities = ner.extract_entities(text, min_confidence=min_entity_confidence)
        all_entities.extend(entities)
        
        # Extract relations
        if len(entities) >= 2:  # Need at least 2 entities for relations
            relations = re_extractor.extract_relations(
                text,
                entities,
                min_confidence=min_relation_confidence
            )
            all_relations.extend(relations)
    
    return all_entities, all_relations


def build_knowledge_graph(relations: List) -> KnowledgeGraph:
    """
    Build knowledge graph from relations.
    
    Args:
        relations: List of Relation objects
    
    Returns:
        KnowledgeGraph object
    """
    print("\nBuilding knowledge graph...")
    kg = KnowledgeGraph()
    kg.build_from_relations(relations)
    return kg


def save_results(
    kg: KnowledgeGraph,
    all_entities: List,
    all_relations: List,
    output_dir: Path
) -> None:
    """
    Save all results to files.
    
    Args:
        kg: Knowledge graph
        all_entities: List of all entities
        all_relations: List of all relations
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save knowledge graph
    print(f"\nSaving knowledge graph to {output_dir / 'knowledge_graph.json'}...")
    kg.save_to_json(output_dir / 'knowledge_graph.json')
    
    # Save entity statistics
    entity_stats = {}
    for entity in all_entities:
        key = (entity.normalized_text, entity.entity_type)
        if key not in entity_stats:
            entity_stats[key] = {
                'text': entity.text,
                'type': entity.entity_type,
                'frequency': 0,
                'avg_confidence': 0.0,
                'confidences': []
            }
        entity_stats[key]['frequency'] += 1
        entity_stats[key]['confidences'].append(entity.confidence)
    
    # Calculate average confidences
    for key in entity_stats:
        confidences = entity_stats[key]['confidences']
        entity_stats[key]['avg_confidence'] = sum(confidences) / len(confidences)
        del entity_stats[key]['confidences']  # Remove raw confidences
    
    # Sort by frequency
    entity_list = sorted(
        entity_stats.values(),
        key=lambda x: x['frequency'],
        reverse=True
    )
    
    with open(output_dir / 'entity_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(entity_list, f, indent=2, ensure_ascii=False)
    
    print(f"Saved entity statistics to {output_dir / 'entity_statistics.json'}")
    
    # Save relation triples
    triples = []
    for relation in all_relations:
        triple = relation.to_dict()
        triples.append(triple)
    
    with open(output_dir / 'relation_triples.json', 'w', encoding='utf-8') as f:
        json.dump(triples, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(triples)} relation triples to {output_dir / 'relation_triples.json'}")
    
    # Save top entities
    top_entities = kg.get_top_entities(n=50)
    top_entities_data = []
    for node_id, props in top_entities:
        props_copy = props.copy()
        props_copy['node_id'] = node_id
        props_copy['degree'] = kg.graph.degree(node_id)
        top_entities_data.append(props_copy)
    
    with open(output_dir / 'top_entities.json', 'w', encoding='utf-8') as f:
        json.dump(top_entities_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved top 50 entities to {output_dir / 'top_entities.json'}")


def main():
    """Main pipeline execution."""
    
    # Configuration
    crawler_root = Path(__file__).parent.parent
    data_file = crawler_root / 'data' / 'processed' / 'posts.jsonl'
    gazetteer_dir = crawler_root / 'ner' / 'gazetteers'
    output_dir = crawler_root / 'kg' / 'output'
    
    # Parameters
    post_limit = None  # None = process all posts
    min_entity_confidence = 0.5
    min_relation_confidence = 0.3
    max_entity_distance = 200
    
    print("=" * 80)
    print("KNOWLEDGE GRAPH CONSTRUCTION PIPELINE")
    print("=" * 80)
    print(f"\nData file: {data_file}")
    print(f"Gazetteer directory: {gazetteer_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Post limit: {post_limit or 'All'}")
    print(f"Min entity confidence: {min_entity_confidence}")
    print(f"Min relation confidence: {min_relation_confidence}")
    print(f"Max entity distance: {max_entity_distance}")
    
    # Initialize extractors
    print("\nInitializing extractors...")
    ner = EntityExtractor(gazetteer_dir)
    re_extractor = RelationExtractor(max_entity_distance=max_entity_distance)
    
    # Load posts
    print(f"\nLoading posts from {data_file}...")
    posts = load_posts(data_file, limit=post_limit)
    print(f"Loaded {len(posts)} posts")
    
    # Process posts
    all_entities, all_relations = process_posts(
        posts,
        ner,
        re_extractor,
        min_entity_confidence,
        min_relation_confidence
    )
    
    print("\nExtraction complete:")
    print(f"  Total entities: {len(all_entities)}")
    print(f"  Total relations: {len(all_relations)}")
    
    # Build knowledge graph
    kg = build_knowledge_graph(all_relations)
    
    # Display statistics
    print("\n" + visualize_graph_statistics(kg))
    
    # Save results
    save_results(kg, all_entities, all_relations, output_dir)
    
    # Display top entities
    print("\nTop 10 most connected entities:")
    top_10 = kg.get_top_entities(n=10)
    for i, (node_id, props) in enumerate(top_10, 1):
        degree = kg.graph.degree(node_id)
        print(f"{i}. {props['text']} ({props['entity_type']}) - degree: {degree}")
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
