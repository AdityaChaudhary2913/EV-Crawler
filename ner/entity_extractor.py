"""
Entity Extractor for EV domain.
Combines gazetteer-based and pattern-based entity recognition.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .patterns import (
    NERPatterns,
    GazetteerPatterns,
    EntityPattern,
    create_negation_patterns,
    should_exclude_entity
)


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str  # The entity text as it appears in the document
    normalized_text: str  # Normalized form (e.g., lowercase, whitespace normalized)
    entity_type: str  # PERSON, ORGANIZATION, PRODUCT, LOCATION, TECHNOLOGY, POLICY
    start: int  # Character offset start
    end: int  # Character offset end
    confidence: float  # Confidence score (0.0 to 1.0)
    source: str  # "gazetteer" or "pattern"
    pattern_name: str = ""  # Which pattern matched (for debugging)
    
    def __hash__(self):
        """Make Entity hashable for deduplication."""
        return hash((self.normalized_text, self.entity_type, self.start, self.end))
    
    def __eq__(self, other):
        """Check equality based on normalized text, type, and position."""
        if not isinstance(other, Entity):
            return False
        return (
            self.normalized_text == other.normalized_text and
            self.entity_type == other.entity_type and
            self.start == other.start and
            self.end == other.end
        )


class EntityExtractor:
    """
    Main entity extraction class.
    Combines gazetteer matching with regex pattern matching.
    """
    
    def __init__(self, gazetteer_dir: Path):
        """
        Initialize the entity extractor.
        
        Args:
            gazetteer_dir: Path to directory containing gazetteer JSON files
        """
        self.gazetteer_dir = Path(gazetteer_dir)
        self.gazetteers = self._load_gazetteers()
        self.gazetteer_patterns = self._build_gazetteer_patterns()
        self.regex_patterns = NERPatterns()
        self.negation_patterns = create_negation_patterns()
        
        # Combine all patterns (gazetteer patterns have higher priority)
        self.all_patterns = self.gazetteer_patterns + self.regex_patterns.get_all_patterns()
        self.all_patterns.sort(key=lambda x: x.priority, reverse=True)
    
    def _load_gazetteers(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load all gazetteer files.
        
        Returns:
            Dictionary mapping file name to its contents
        """
        gazetteers = {}
        
        gazetteer_files = {
            'organizations': 'organizations.json',
            'products': 'products.json',
            'locations': 'locations.json',
            'technologies': 'technologies.json',
            'policies': 'policies.json'
        }
        
        for key, filename in gazetteer_files.items():
            file_path = self.gazetteer_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    gazetteers[key] = json.load(f)
            else:
                print(f"Warning: Gazetteer file not found: {file_path}")
                gazetteers[key] = {}
        
        return gazetteers
    
    def _build_gazetteer_patterns(self) -> List[EntityPattern]:
        """
        Build regex patterns from loaded gazetteers.
        
        Returns:
            List of EntityPattern objects with high priority
        """
        patterns = []
        
        # Organizations (priority 15 - highest)
        if self.gazetteers.get('organizations'):
            for category, terms in self.gazetteers['organizations'].items():
                pattern = GazetteerPatterns.build_pattern_from_list(
                    entity_type="ORGANIZATION",
                    terms=terms,
                    priority=15
                )
                patterns.append(pattern)
        
        # Products (priority 14)
        if self.gazetteers.get('products'):
            for category, terms in self.gazetteers['products'].items():
                pattern = GazetteerPatterns.build_pattern_from_list(
                    entity_type="PRODUCT",
                    terms=terms,
                    priority=14
                )
                patterns.append(pattern)
        
        # Technologies (priority 13)
        if self.gazetteers.get('technologies'):
            for category, terms in self.gazetteers['technologies'].items():
                pattern = GazetteerPatterns.build_pattern_from_list(
                    entity_type="TECHNOLOGY",
                    terms=terms,
                    priority=13
                )
                patterns.append(pattern)
        
        # Locations (priority 12)
        if self.gazetteers.get('locations'):
            for category, terms in self.gazetteers['locations'].items():
                pattern = GazetteerPatterns.build_pattern_from_list(
                    entity_type="LOCATION",
                    terms=terms,
                    priority=12
                )
                patterns.append(pattern)
        
        # Policies (priority 11)
        if self.gazetteers.get('policies'):
            for category, terms in self.gazetteers['policies'].items():
                pattern = GazetteerPatterns.build_pattern_from_list(
                    entity_type="POLICY",
                    terms=terms,
                    priority=11
                )
                patterns.append(pattern)
        
        return patterns
    
    def extract_entities(self, text: str, min_confidence: float = 0.5) -> List[Entity]:
        """
        Extract all entities from text.
        
        Args:
            text: Input text to extract entities from
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
        
        Returns:
            List of Entity objects sorted by start position
        """
        entities = []
        
        # Track which spans have been matched to avoid overlaps
        matched_spans = []
        
        # Apply all patterns in priority order
        for pattern_obj in self.all_patterns:
            for match in pattern_obj.pattern.finditer(text):
                start = match.start()
                end = match.end()
                
                # Check if this span overlaps with higher-priority match
                if self._overlaps_with_existing(start, end, matched_spans):
                    continue
                
                # Check negation patterns
                if should_exclude_entity(text, start, end, self.negation_patterns):
                    continue
                
                # Extract the matched text
                matched_text = match.group(0)
                
                # Determine source and confidence
                source = "gazetteer" if pattern_obj.priority >= 11 else "pattern"
                confidence = self._calculate_confidence(
                    matched_text,
                    pattern_obj.entity_type,
                    source,
                    pattern_obj.priority
                )
                
                if confidence < min_confidence:
                    continue
                
                # Create entity
                entity = Entity(
                    text=matched_text,
                    normalized_text=self._normalize_text(matched_text),
                    entity_type=pattern_obj.entity_type,
                    start=start,
                    end=end,
                    confidence=confidence,
                    source=source,
                    pattern_name=f"{pattern_obj.entity_type}_{pattern_obj.priority}"
                )
                
                entities.append(entity)
                matched_spans.append((start, end))
        
        # Deduplicate entities (same text, type, position)
        entities = list(set(entities))
        
        # Sort by start position
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    def _overlaps_with_existing(
        self,
        start: int,
        end: int,
        matched_spans: List[Tuple[int, int]]
    ) -> bool:
        """
        Check if a span overlaps with any existing matched spans.
        
        Args:
            start: Start position of new span
            end: End position of new span
            matched_spans: List of (start, end) tuples for already matched spans
        
        Returns:
            True if overlaps, False otherwise
        """
        for existing_start, existing_end in matched_spans:
            # Check for any overlap
            if not (end <= existing_start or start >= existing_end):
                return True
        return False
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize entity text for comparison.
        
        Args:
            text: Raw entity text
        
        Returns:
            Normalized text (lowercase, whitespace normalized)
        """
        # Convert to lowercase
        normalized = text.lower()
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove trailing punctuation
        normalized = normalized.rstrip('.,;:!?')
        
        return normalized
    
    def _calculate_confidence(
        self,
        text: str,
        entity_type: str,
        source: str,
        priority: int
    ) -> float:
        """
        Calculate confidence score for an entity.
        
        Factors:
        - Source (gazetteer = higher confidence)
        - Pattern priority
        - Text characteristics (length, capitalization)
        
        Args:
            text: Entity text
            entity_type: Type of entity
            source: "gazetteer" or "pattern"
            priority: Pattern priority
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Source bonus
        if source == "gazetteer":
            confidence += 0.3
        
        # Priority bonus (normalize priority to 0-0.2 range)
        priority_bonus = min(priority / 15.0 * 0.2, 0.2)
        confidence += priority_bonus
        
        # Length bonus (longer entities tend to be more reliable)
        if len(text) >= 10:
            confidence += 0.05
        elif len(text) <= 2:
            confidence -= 0.1
        
        # Capitalization bonus (for certain entity types)
        if entity_type in ["ORGANIZATION", "PERSON", "LOCATION", "PRODUCT"]:
            if text[0].isupper():
                confidence += 0.05
        
        # Ensure confidence is in [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def extract_and_group_entities(self, text: str) -> Dict[str, List[Entity]]:
        """
        Extract entities and group by type.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary mapping entity type to list of entities
        """
        entities = self.extract_entities(text)
        
        grouped = defaultdict(list)
        for entity in entities:
            grouped[entity.entity_type].append(entity)
        
        return dict(grouped)
    
    def get_statistics(self, entities: List[Entity]) -> Dict:
        """
        Calculate statistics about extracted entities.
        
        Args:
            entities: List of entities
        
        Returns:
            Dictionary with statistics
        """
        if not entities:
            return {
                'total_entities': 0,
                'by_type': {},
                'by_source': {},
                'avg_confidence': 0.0
            }
        
        by_type = defaultdict(int)
        by_source = defaultdict(int)
        total_confidence = 0.0
        
        for entity in entities:
            by_type[entity.entity_type] += 1
            by_source[entity.source] += 1
            total_confidence += entity.confidence
        
        return {
            'total_entities': len(entities),
            'by_type': dict(by_type),
            'by_source': dict(by_source),
            'avg_confidence': total_confidence / len(entities)
        }


def visualize_entities(text: str, entities: List[Entity]) -> str:
    """
    Create a visual representation of entities in text.
    Useful for debugging and evaluation.
    
    Args:
        text: Original text
        entities: List of extracted entities
    
    Returns:
        Text with entity annotations
    """
    # Sort entities by start position
    sorted_entities = sorted(entities, key=lambda x: x.start)
    
    # Build annotated text
    result = []
    last_end = 0
    
    for entity in sorted_entities:
        # Add text before entity
        result.append(text[last_end:entity.start])
        
        # Add annotated entity
        result.append(f"[{entity.text}]({entity.entity_type}:{entity.confidence:.2f})")
        
        last_end = entity.end
    
    # Add remaining text
    result.append(text[last_end:])
    
    return ''.join(result)
