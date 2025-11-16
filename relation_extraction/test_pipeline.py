"""
Test the complete NER + RE pipeline.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import EntityExtractor
from relation_extraction.relation_extractor import RelationExtractor


def test_pipeline():
    """Test NER + RE pipeline on sample texts."""
    
    # Initialize extractors
    gazetteer_dir = Path(__file__).parent.parent / 'ner' / 'gazetteers'
    ner = EntityExtractor(gazetteer_dir)
    re_extractor = RelationExtractor(max_entity_distance=200)
    
    # Test cases
    test_texts = [
        "Tesla produces Model 3 which features a 75 kWh battery and supports DC fast charging.",
        
        "Ford F-150 Lightning competes with Rivian R1T in the electric truck market.",
        
        "Ather manufactures the 450X with support for Ather Grid charging network in Bangalore.",
        
        "The Inflation Reduction Act provides a $7500 tax credit that benefits Tesla and Ford.",
        
        "BYD develops solid-state battery technology at its facility in Shenzhen, China.",
        
        "Tata Nexon EV uses LFP battery technology and is available in Delhi and Mumbai.",
        
        "California ZEV mandate affects automakers including Tesla, Ford, and GM.",
        
        "ChargePoint partners with Electrify America to install 350 kW chargers across the US.",
        
        "Elon Musk announced Full Self-Driving improvements for Model Y produced at Gigafactory.",
        
        "Ola S1 Pro benefits from FAME-II subsidy when sold in India."
    ]
    
    print("=" * 80)
    print("NER + RE PIPELINE TEST")
    print("=" * 80)
    print()
    
    all_relations = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"Text: {text}")
        print()
        
        # Extract entities
        entities = ner.extract_entities(text, min_confidence=0.5)
        print(f"Entities found: {len(entities)}")
        for entity in entities:
            print(f"  - {entity.text} ({entity.entity_type})")
        print()
        
        # Extract relations
        relations = re_extractor.extract_relations(text, entities, min_confidence=0.3)
        all_relations.extend(relations)
        
        print(f"Relations found: {len(relations)}")
        for relation in relations:
            print(
                f"  - {relation.entity1.text} --[{relation.relation_type}]--> "
                f"{relation.entity2.text} (conf: {relation.confidence:.2f})"
            )
        
        print()
        print("-" * 80)
        print()
    
    # Overall statistics
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    
    # Entity statistics
    all_entities = []
    for text in test_texts:
        all_entities.extend(ner.extract_entities(text, min_confidence=0.5))
    
    entity_stats = ner.get_statistics(all_entities)
    print(f"\nTotal entities: {entity_stats['total_entities']}")
    print("Entities by type:")
    for etype, count in sorted(entity_stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {etype}: {count}")
    
    # Relation statistics
    relation_stats = re_extractor.get_statistics(all_relations)
    print(f"\nTotal relations: {relation_stats['total_relations']}")
    print("Relations by type:")
    for rtype, count in sorted(relation_stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {rtype}: {count}")
    print(f"\nUnique triples: {relation_stats['unique_triples']}")
    print(f"Average relation confidence: {relation_stats['avg_confidence']:.3f}")
    print()
    
    # Sample triples
    print("Sample triples (first 15):")
    for i, relation in enumerate(all_relations[:15], 1):
        triple = relation.to_triple()
        print(f"{i}. ({triple[0]}, {triple[1]}, {triple[2]})")
    print()


if __name__ == '__main__':
    test_pipeline()
