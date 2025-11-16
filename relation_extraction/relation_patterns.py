"""
Relation extraction patterns for EV domain.
Defines rules and patterns for extracting relationships between entities.
"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class RelationPattern:
    """Represents a pattern for relation extraction."""
    relation_type: str  # PRODUCES, DISCUSSES, HAS_FEATURE, etc.
    pattern: re.Pattern  # Compiled regex pattern
    entity1_type: List[str]  # Allowed types for first entity
    entity2_type: List[str]  # Allowed types for second entity
    confidence_base: float  # Base confidence for this pattern
    bidirectional: bool = False  # Can relation go both ways?


class RelationPatterns:
    """
    Defines patterns for extracting relations between entities.
    Uses regex patterns with entity placeholders.
    """
    
    def __init__(self):
        """Initialize all relation patterns."""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[RelationPattern]:
        """Build all relation patterns."""
        patterns = []
        
        # PRODUCES: Manufacturer produces vehicle/product
        patterns.extend([
            RelationPattern(
                relation_type="PRODUCES",
                pattern=re.compile(
                    r'\{E1\}\s+(?:makes?|produces?|manufactures?|launches?|announced?|unveiled?|released?)\s+(?:the\s+)?'
                    r'(?:new\s+)?(?:electric\s+)?(?:vehicle\s+)?(?:model\s+)?\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["PRODUCT"],
                confidence_base=0.9
            ),
            RelationPattern(
                relation_type="PRODUCES",
                pattern=re.compile(
                    r'\{E2\}\s+(?:from|by|made by)\s+\{E1\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["PRODUCT"],
                confidence_base=0.85
            ),
            RelationPattern(
                relation_type="PRODUCES",
                pattern=re.compile(
                    r'\{E1\}(?:\'s)?\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["PRODUCT"],
                confidence_base=0.7
            ),
        ])
        
        # HAS_FEATURE: Product has technology/feature
        patterns.extend([
            RelationPattern(
                relation_type="HAS_FEATURE",
                pattern=re.compile(
                    r'\{E1\}\s+(?:has|features?|includes?|comes with|equipped with|supports?|uses?)\s+'
                    r'(?:a\s+)?(?:an\s+)?\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["PRODUCT"],
                entity2_type=["TECHNOLOGY"],
                confidence_base=0.9
            ),
            RelationPattern(
                relation_type="HAS_FEATURE",
                pattern=re.compile(
                    r'\{E2\}\s+(?:in|on|for)\s+(?:the\s+)?\{E1\}',
                    re.IGNORECASE
                ),
                entity1_type=["PRODUCT"],
                entity2_type=["TECHNOLOGY"],
                confidence_base=0.75
            ),
        ])
        
        # COMPETES_WITH: Product/Organization competes with another
        patterns.extend([
            RelationPattern(
                relation_type="COMPETES_WITH",
                pattern=re.compile(
                    r'\{E1\}\s+(?:competes? with|rivals?|challenges?|vs\.?|versus)\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["ORGANIZATION", "PRODUCT"],
                confidence_base=0.9,
                bidirectional=True
            ),
            RelationPattern(
                relation_type="COMPETES_WITH",
                pattern=re.compile(
                    r'\{E1\}\s+(?:and|or)\s+\{E2\}\s+(?:are\s+)?(?:competing|rivals?)',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["ORGANIZATION", "PRODUCT"],
                confidence_base=0.85,
                bidirectional=True
            ),
        ])
        
        # LOCATED_IN: Organization/Production located in place
        patterns.extend([
            RelationPattern(
                relation_type="LOCATED_IN",
                pattern=re.compile(
                    r'\{E1\}\s+(?:in|at|based in|headquartered in|located in)\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["LOCATION"],
                confidence_base=0.9
            ),
            RelationPattern(
                relation_type="LOCATED_IN",
                pattern=re.compile(
                    r'(?:in|at)\s+\{E2\},?\s+\{E1\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["LOCATION"],
                confidence_base=0.75
            ),
        ])
        
        # AVAILABLE_IN: Product available in location
        patterns.extend([
            RelationPattern(
                relation_type="AVAILABLE_IN",
                pattern=re.compile(
                    r'\{E1\}\s+(?:available|launched|released|sold)\s+(?:in|at)\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["PRODUCT"],
                entity2_type=["LOCATION"],
                confidence_base=0.85
            ),
        ])
        
        # USES: Organization uses technology
        patterns.extend([
            RelationPattern(
                relation_type="USES",
                pattern=re.compile(
                    r'\{E1\}\s+(?:uses?|utilizes?|employs?|adopts?|integrates?)\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["TECHNOLOGY"],
                confidence_base=0.9
            ),
        ])
        
        # AFFECTED_BY: Product/Organization affected by policy
        patterns.extend([
            RelationPattern(
                relation_type="AFFECTED_BY",
                pattern=re.compile(
                    r'\{E2\}\s+(?:affects?|impacts?|influences?|changes?)\s+\{E1\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["POLICY"],
                confidence_base=0.85
            ),
            RelationPattern(
                relation_type="AFFECTED_BY",
                pattern=re.compile(
                    r'\{E1\}\s+(?:under|due to|because of|thanks to)\s+(?:the\s+)?\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["POLICY"],
                confidence_base=0.8
            ),
        ])
        
        # BENEFITS_FROM: Organization/Product benefits from policy
        patterns.extend([
            RelationPattern(
                relation_type="BENEFITS_FROM",
                pattern=re.compile(
                    r'\{E1\}\s+(?:benefits?|qualifies?|eligible)\s+(?:from|for|under)\s+(?:the\s+)?\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["POLICY"],
                confidence_base=0.9
            ),
            RelationPattern(
                relation_type="BENEFITS_FROM",
                pattern=re.compile(
                    r'\{E2\}\s+(?:provides?|offers?)\s+(?:a\s+)?(?:subsidy|credit|incentive)\s+(?:for|to)\s+\{E1\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION", "PRODUCT"],
                entity2_type=["POLICY"],
                confidence_base=0.85
            ),
        ])
        
        # DISCUSSES: Text discusses topic (entity co-occurrence)
        patterns.extend([
            RelationPattern(
                relation_type="DISCUSSES",
                pattern=re.compile(
                    r'\{E1\}.*?\{E2\}',  # Simple co-occurrence within text
                    re.IGNORECASE | re.DOTALL
                ),
                entity1_type=["ORGANIZATION", "PRODUCT", "TECHNOLOGY", "LOCATION", "POLICY"],
                entity2_type=["ORGANIZATION", "PRODUCT", "TECHNOLOGY", "LOCATION", "POLICY"],
                confidence_base=0.5,  # Low confidence for simple co-occurrence
                bidirectional=True
            ),
        ])
        
        # DEVELOPS: Organization develops technology
        patterns.extend([
            RelationPattern(
                relation_type="DEVELOPS",
                pattern=re.compile(
                    r'\{E1\}\s+(?:develops?|developing|created?|invented?|pioneered?)\s+(?:a\s+)?(?:an\s+)?\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["TECHNOLOGY"],
                confidence_base=0.9
            ),
        ])
        
        # PARTNERS_WITH: Organization partners with organization
        patterns.extend([
            RelationPattern(
                relation_type="PARTNERS_WITH",
                pattern=re.compile(
                    r'\{E1\}\s+(?:partners?|partnering|collaborates?|teams up|works)\s+(?:with|together with)\s+\{E2\}',
                    re.IGNORECASE
                ),
                entity1_type=["ORGANIZATION"],
                entity2_type=["ORGANIZATION"],
                confidence_base=0.9,
                bidirectional=True
            ),
        ])
        
        return patterns
    
    def get_patterns_for_entity_types(
        self,
        type1: str,
        type2: str
    ) -> List[RelationPattern]:
        """
        Get all patterns applicable to a pair of entity types.
        
        Args:
            type1: Type of first entity
            type2: Type of second entity
        
        Returns:
            List of applicable RelationPattern objects
        """
        applicable_patterns = []
        
        for pattern in self.patterns:
            # Check if entity types match
            if type1 in pattern.entity1_type and type2 in pattern.entity2_type:
                applicable_patterns.append(pattern)
            # Check reverse if bidirectional
            elif pattern.bidirectional and type2 in pattern.entity1_type and type1 in pattern.entity2_type:
                applicable_patterns.append(pattern)
        
        return applicable_patterns
    
    def get_all_patterns(self) -> List[RelationPattern]:
        """Get all relation patterns."""
        return self.patterns
    
    def get_relation_types(self) -> List[str]:
        """Get list of all relation types."""
        return list(set(p.relation_type for p in self.patterns))


def create_distance_based_confidence(distance: int, max_distance: int = 100) -> float:
    """
    Calculate confidence based on distance between entities.
    Closer entities are more likely to be related.
    
    Args:
        distance: Character distance between entities
        max_distance: Maximum distance to consider
    
    Returns:
        Distance-based confidence modifier (0.0 to 1.0)
    """
    if distance > max_distance:
        return 0.1
    
    # Linear decay
    return 1.0 - (distance / max_distance) * 0.5


def create_sentence_based_confidence(
    entity1_start: int,
    entity2_start: int,
    text: str
) -> float:
    """
    Calculate confidence based on whether entities are in same sentence.
    
    Args:
        entity1_start: Start position of first entity
        entity2_start: Start position of second entity
        text: Full text
    
    Returns:
        Sentence-based confidence modifier
    """
    # Simple sentence detection (split on . ! ?)
    sentences = re.split(r'[.!?]+', text)
    
    # Find which sentence each entity is in
    current_pos = 0
    entity1_sentence = -1
    entity2_sentence = -1
    
    for i, sentence in enumerate(sentences):
        sentence_end = current_pos + len(sentence)
        
        if current_pos <= entity1_start < sentence_end:
            entity1_sentence = i
        if current_pos <= entity2_start < sentence_end:
            entity2_sentence = i
        
        current_pos = sentence_end + 1  # +1 for punctuation
    
    # Same sentence = high confidence
    if entity1_sentence == entity2_sentence and entity1_sentence != -1:
        return 1.0
    # Adjacent sentences = medium confidence
    elif abs(entity1_sentence - entity2_sentence) == 1:
        return 0.7
    # Different sentences = lower confidence
    else:
        return 0.4
