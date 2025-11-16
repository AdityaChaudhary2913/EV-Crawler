"""
Test the NER system on sample EV-related text.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import EntityExtractor, visualize_entities


def test_ner():
    """Test NER on sample texts."""
    
    # Initialize extractor
    gazetteer_dir = Path(__file__).parent.parent / 'ner' / 'gazetteers'
    extractor = EntityExtractor(gazetteer_dir)
    
    # Test cases from EV domain
    test_texts = [
        "Tesla Model 3 has a 75 kWh battery and supports 250 kW DC fast charging using CCS2.",
        
        "Ather 450X launched in Bangalore with support for Ather Grid charging network.",
        
        "The Inflation Reduction Act provides a $7500 tax credit for qualifying EVs.",
        
        "Ford F-150 Lightning competes with Rivian R1T in the electric truck market.",
        
        "BYD is expanding its solid-state battery production in Shenzhen, China.",
        
        "FAME-II subsidy reduced in Delhi and Mumbai affecting Ola S1 Pro sales.",
        
        "Elon Musk announced Full Self-Driving improvements for Model Y at the Gigafactory.",
        
        "California ZEV mandate requires automakers to increase EV sales by 2030.",
        
        "ChargePoint and Electrify America are installing 350 kW ultra-fast chargers across the US.",
        
        "Tata Nexon EV uses LFP battery technology with thermal management system."
    ]
    
    print("=" * 80)
    print("NER SYSTEM TEST")
    print("=" * 80)
    print()
    
    all_entities = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"Text: {text}")
        print()
        
        # Extract entities
        entities = extractor.extract_entities(text, min_confidence=0.5)
        all_entities.extend(entities)
        
        # Group by type
        by_type = {}
        for entity in entities:
            if entity.entity_type not in by_type:
                by_type[entity.entity_type] = []
            by_type[entity.entity_type].append(entity)
        
        # Print results
        print(f"Found {len(entities)} entities:")
        for entity_type in sorted(by_type.keys()):
            print(f"  {entity_type}:")
            for entity in by_type[entity_type]:
                print(f"    - {entity.text} (confidence: {entity.confidence:.2f}, source: {entity.source})")
        
        # Visualized output
        print()
        print("Annotated:")
        print(visualize_entities(text, entities))
        print()
        print("-" * 80)
        print()
    
    # Overall statistics
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    stats = extractor.get_statistics(all_entities)
    print(f"Total entities extracted: {stats['total_entities']}")
    print()
    print("By entity type:")
    for entity_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {entity_type}: {count}")
    print()
    print("By source:")
    for source, count in stats['by_source'].items():
        print(f"  {source}: {count}")
    print()
    print(f"Average confidence: {stats['avg_confidence']:.3f}")
    print()


if __name__ == '__main__':
    test_ner()
