"""
Relation Extractor for EV domain.
Extracts relationships between entities using pattern matching.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from itertools import combinations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ner.entity_extractor import Entity
from relation_extraction.relation_patterns import (
    RelationPatterns,
    create_distance_based_confidence,
    create_sentence_based_confidence
)


@dataclass
class Relation:
    """Represents an extracted relation between two entities."""
    entity1: Entity  # Subject entity
    entity2: Entity  # Object entity
    relation_type: str  # Type of relation
    confidence: float  # Confidence score (0.0 to 1.0)
    context: str  # Text snippet showing the relation
    pattern_name: str = ""  # Which pattern matched (for debugging)
    
    def to_triple(self) -> Tuple[str, str, str]:
        """Convert to (subject, predicate, object) triple."""
        return (
            self.entity1.normalized_text,
            self.relation_type,
            self.entity2.normalized_text
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'subject': self.entity1.normalized_text,
            'subject_type': self.entity1.entity_type,
            'predicate': self.relation_type,
            'object': self.entity2.normalized_text,
            'object_type': self.entity2.entity_type,
            'confidence': self.confidence,
            'context': self.context
        }


class RelationExtractor:
    """
    Extract relations between entities using pattern matching.
    No ML models or predefined libraries - pure rule-based approach.
    """
    
    def __init__(self, max_entity_distance: int = 200):
        """
        Initialize relation extractor.
        
        Args:
            max_entity_distance: Maximum character distance between entities to consider
        """
        self.relation_patterns = RelationPatterns()
        self.max_entity_distance = max_entity_distance
    
    def extract_relations(
        self,
        text: str,
        entities: List[Entity],
        min_confidence: float = 0.5
    ) -> List[Relation]:
        """
        Extract all relations between entities in text.
        
        Args:
            text: Original text containing entities
            entities: List of extracted entities
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of Relation objects
        """
        relations = []
        
        # Consider all pairs of entities
        for entity1, entity2 in combinations(entities, 2):
            # Skip if entities are too far apart
            distance = abs(entity1.start - entity2.start)
            if distance > self.max_entity_distance:
                continue
            
            # Try to extract relations for this pair
            pair_relations = self._extract_relations_for_pair(
                text, entity1, entity2, min_confidence
            )
            relations.extend(pair_relations)
            
            # Also try reverse order (entity2, entity1)
            reverse_relations = self._extract_relations_for_pair(
                text, entity2, entity1, min_confidence
            )
            relations.extend(reverse_relations)
        
        # Deduplicate and sort by confidence
        relations = self._deduplicate_relations(relations)
        relations.sort(key=lambda r: r.confidence, reverse=True)
        
        return relations
    
    def _extract_relations_for_pair(
        self,
        text: str,
        entity1: Entity,
        entity2: Entity,
        min_confidence: float
    ) -> List[Relation]:
        """
        Try to extract relations between a specific pair of entities.
        
        Args:
            text: Full text
            entity1: First entity (subject)
            entity2: Second entity (object)
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of relations found
        """
        relations = []
        
        # Get applicable patterns for these entity types
        patterns = self.relation_patterns.get_patterns_for_entity_types(
            entity1.entity_type,
            entity2.entity_type
        )
        
        if not patterns:
            return relations
        
        # Extract context (text between and around entities)
        context_start = min(entity1.start, entity2.start)
        context_end = max(entity1.end, entity2.end)
        
        # Expand context to include surrounding words
        context_start = max(0, context_start - 50)
        context_end = min(len(text), context_end + 50)
        context = text[context_start:context_end]
        
        # Try each pattern
        for pattern_obj in patterns:
            # Create pattern with entity placeholders replaced
            pattern_str = pattern_obj.pattern.pattern
            
            # Escape special regex characters in entity text
            e1_escaped = re.escape(entity1.text)
            e2_escaped = re.escape(entity2.text)
            
            # Replace placeholders
            pattern_str = pattern_str.replace(r'\{E1\}', e1_escaped)
            pattern_str = pattern_str.replace(r'\{E2\}', e2_escaped)
            
            # Compile and match
            try:
                pattern_compiled = re.compile(pattern_str, re.IGNORECASE)
                match = pattern_compiled.search(context)
                
                if match:
                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        pattern_obj.confidence_base,
                        entity1,
                        entity2,
                        text
                    )
                    
                    if confidence >= min_confidence:
                        relation = Relation(
                            entity1=entity1,
                            entity2=entity2,
                            relation_type=pattern_obj.relation_type,
                            confidence=confidence,
                            context=match.group(0),
                            pattern_name=pattern_obj.relation_type
                        )
                        relations.append(relation)
            except re.error:
                # Skip patterns that fail to compile
                continue
        
        return relations
    
    def _calculate_confidence(
        self,
        base_confidence: float,
        entity1: Entity,
        entity2: Entity,
        text: str
    ) -> float:
        """
        Calculate final confidence score for a relation.
        
        Factors:
        - Base confidence from pattern
        - Entity confidence scores
        - Distance between entities
        - Same sentence bonus
        
        Args:
            base_confidence: Base confidence from pattern
            entity1: First entity
            entity2: Second entity
            text: Full text
        
        Returns:
            Final confidence score
        """
        # Start with base confidence
        confidence = base_confidence
        
        # Factor in entity confidences
        entity_conf = (entity1.confidence + entity2.confidence) / 2.0
        confidence *= entity_conf
        
        # Distance-based modifier
        distance = abs(entity1.start - entity2.start)
        distance_conf = create_distance_based_confidence(distance, self.max_entity_distance)
        confidence *= distance_conf
        
        # Sentence-based modifier
        sentence_conf = create_sentence_based_confidence(
            entity1.start,
            entity2.start,
            text
        )
        confidence *= sentence_conf
        
        # Ensure confidence is in [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def _deduplicate_relations(self, relations: List[Relation]) -> List[Relation]:
        """
        Remove duplicate relations, keeping highest confidence.
        
        Args:
            relations: List of relations (may contain duplicates)
        
        Returns:
            Deduplicated list
        """
        # Group by (entity1, relation_type, entity2)
        relation_dict = {}
        
        for relation in relations:
            key = (
                relation.entity1.normalized_text,
                relation.relation_type,
                relation.entity2.normalized_text
            )
            
            # Keep relation with highest confidence
            if key not in relation_dict or relation.confidence > relation_dict[key].confidence:
                relation_dict[key] = relation
        
        return list(relation_dict.values())
    
    def extract_and_group_relations(
        self,
        text: str,
        entities: List[Entity],
        min_confidence: float = 0.5
    ) -> Dict[str, List[Relation]]:
        """
        Extract relations and group by type.
        
        Args:
            text: Input text
            entities: List of entities
            min_confidence: Minimum confidence threshold
        
        Returns:
            Dictionary mapping relation type to list of relations
        """
        relations = self.extract_relations(text, entities, min_confidence)
        
        grouped = {}
        for relation in relations:
            if relation.relation_type not in grouped:
                grouped[relation.relation_type] = []
            grouped[relation.relation_type].append(relation)
        
        return grouped
    
    def get_statistics(self, relations: List[Relation]) -> Dict:
        """
        Calculate statistics about extracted relations.
        
        Args:
            relations: List of relations
        
        Returns:
            Dictionary with statistics
        """
        if not relations:
            return {
                'total_relations': 0,
                'by_type': {},
                'avg_confidence': 0.0,
                'unique_triples': 0
            }
        
        by_type = {}
        for relation in relations:
            if relation.relation_type not in by_type:
                by_type[relation.relation_type] = 0
            by_type[relation.relation_type] += 1
        
        total_confidence = sum(r.confidence for r in relations)
        unique_triples = len(set(r.to_triple() for r in relations))
        
        return {
            'total_relations': len(relations),
            'by_type': by_type,
            'avg_confidence': total_confidence / len(relations),
            'unique_triples': unique_triples
        }


def visualize_relations(relations: List[Relation], max_display: int = 20) -> str:
    """
    Create a visual representation of extracted relations.
    
    Args:
        relations: List of relations
        max_display: Maximum number of relations to display
    
    Returns:
        Formatted string representation
    """
    if not relations:
        return "No relations extracted."
    
    output = []
    output.append(f"Extracted {len(relations)} relations:\n")
    
    for i, relation in enumerate(relations[:max_display], 1):
        output.append(
            f"{i}. {relation.entity1.text} --[{relation.relation_type}]--> "
            f"{relation.entity2.text} (confidence: {relation.confidence:.2f})"
        )
        output.append(f"   Context: {relation.context}\n")
    
    if len(relations) > max_display:
        output.append(f"... and {len(relations) - max_display} more relations")
    
    return '\n'.join(output)
