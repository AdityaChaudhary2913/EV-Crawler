"""
Pattern definitions for Named Entity Recognition.
Contains regex patterns for each entity type in the EV domain.
"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class EntityPattern:
    """Represents a pattern for entity extraction."""
    entity_type: str
    pattern: re.Pattern
    priority: int  # Higher priority patterns matched first


class NERPatterns:
    """
    Defines regex patterns for entity extraction.
    No ML models or predefined NER libraries - pure rule-based.
    """
    
    def __init__(self):
        """Initialize all entity patterns."""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[EntityPattern]:
        """
        Build all entity patterns with priorities.
        Higher priority = more specific patterns matched first.
        """
        patterns = []
        
        # PERSON patterns (Priority 10 - highest specificity)
        # Match common name patterns: First Last, First Middle Last, @username
        patterns.append(EntityPattern(
            entity_type="PERSON",
            pattern=re.compile(
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'  # John Smith, John A. Smith
            ),
            priority=10
        ))
        
        patterns.append(EntityPattern(
            entity_type="PERSON",
            pattern=re.compile(r'@(\w+)'),  # Social media handles
            priority=9
        ))
        
        # ORGANIZATION patterns (Priority 8)
        # Match company suffixes
        patterns.append(EntityPattern(
            entity_type="ORGANIZATION",
            pattern=re.compile(
                r'\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\s+'
                r'(?:Inc\.?|Corp\.?|Corporation|Company|Co\.?|Ltd\.?|Limited|Motors?|'
                r'Energy|Electric|Automotive|Group|Technologies|Systems)\b'
            ),
            priority=8
        ))
        
        # PRODUCT patterns (Priority 7)
        # Match model naming patterns: Model + Number/Letter
        patterns.append(EntityPattern(
            entity_type="PRODUCT",
            pattern=re.compile(
                r'\b(?:Model\s+[A-Z0-9]+|[A-Z]+\d+[A-Z]*|'
                r'[A-Z][a-z]+\s+(?:EV|Electric|e-tron|iX|ID\.\d+))\b'
            ),
            priority=7
        ))
        
        # TECHNOLOGY patterns (Priority 6)
        # Match technical terms with units or specific patterns
        patterns.append(EntityPattern(
            entity_type="TECHNOLOGY",
            pattern=re.compile(
                r'\b(?:\d+\s*kWh|\d+\s*kW|\d+\s*hp|\d+\s*mi(?:les)?|'
                r'lithium[- ](?:ion|metal)|solid[- ]state|'
                r'DC\s+fast\s+charging|Level\s+[23]\s+charging|'
                r'CCS[12]?|CHAdeMO|NACS|'
                r'autonomous|autopilot|FSD|ADAS|LiDAR)\b',
                re.IGNORECASE
            ),
            priority=6
        ))
        
        # Battery capacity patterns
        patterns.append(EntityPattern(
            entity_type="TECHNOLOGY",
            pattern=re.compile(r'\b(\d+(?:\.\d+)?\s*kWh)\s+battery\b', re.IGNORECASE),
            priority=8
        ))
        
        # Charging speed patterns
        patterns.append(EntityPattern(
            entity_type="TECHNOLOGY",
            pattern=re.compile(r'\b(\d+\s*kW)\s+(?:charging|charger)\b', re.IGNORECASE),
            priority=8
        ))
        
        # LOCATION patterns (Priority 5)
        # Match location indicators
        patterns.append(EntityPattern(
            entity_type="LOCATION",
            pattern=re.compile(
                r'\b(?:in|at|from|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            ),
            priority=5
        ))
        
        # State/Country patterns
        patterns.append(EntityPattern(
            entity_type="LOCATION",
            pattern=re.compile(
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*(?:[A-Z]{2}|USA|US|India|China)\b'
            ),
            priority=7
        ))
        
        # POLICY patterns (Priority 4)
        # Match policy/regulation terms
        patterns.append(EntityPattern(
            entity_type="POLICY",
            pattern=re.compile(
                r'\b(?:FAME[- ]?II?|IRA|'
                r'\$\d+,?\d*\s+(?:tax\s+)?credit|'
                r'(?:federal|state|EV)\s+(?:subsidy|incentive|credit|mandate)|'
                r'(?:emission|emissions)\s+(?:standard|regulation|target)s?|'
                r'ZEV\s+mandate|PLI\s+scheme|'
                r'(?:EU\s+)?Green\s+Deal|'
                r'\d{4}\s+(?:ICE|combustion\s+engine)\s+ban)\b',
                re.IGNORECASE
            ),
            priority=4
        ))
        
        # NUMERIC patterns (Priority 3)
        # Match measurements and metrics
        patterns.append(EntityPattern(
            entity_type="METRIC",
            pattern=re.compile(
                r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*'
                r'(?:miles?|km|kWh|kW|hp|mph|km/h|%|dollars?|\$)\b',
                re.IGNORECASE
            ),
            priority=3
        ))
        
        # Sort patterns by priority (highest first)
        patterns.sort(key=lambda x: x.priority, reverse=True)
        
        return patterns
    
    def get_patterns_by_type(self, entity_type: str) -> List[EntityPattern]:
        """Get all patterns for a specific entity type."""
        return [p for p in self.patterns if p.entity_type == entity_type]
    
    def get_all_patterns(self) -> List[EntityPattern]:
        """Get all patterns sorted by priority."""
        return self.patterns


# Gazetteer-based patterns
class GazetteerPatterns:
    """
    Build exact-match patterns from gazetteers.
    These have highest priority since they're known entities.
    """
    
    @staticmethod
    def build_pattern_from_list(
        entity_type: str,
        terms: List[str],
        priority: int = 15
    ) -> EntityPattern:
        """
        Build a regex pattern from a list of terms.
        Uses word boundaries and case-insensitive matching.
        """
        # Escape special regex characters
        escaped_terms = [re.escape(term) for term in terms]
        
        # Sort by length (longest first) to match "Model S" before "Model"
        escaped_terms.sort(key=len, reverse=True)
        
        # Build alternation pattern
        pattern_str = r'\b(?:' + '|'.join(escaped_terms) + r')\b'
        
        return EntityPattern(
            entity_type=entity_type,
            pattern=re.compile(pattern_str, re.IGNORECASE),
            priority=priority
        )
    
    @staticmethod
    def build_contextual_pattern(
        entity_type: str,
        terms: List[str],
        context_before: str = '',
        context_after: str = '',
        priority: int = 12
    ) -> EntityPattern:
        """
        Build a pattern with surrounding context.
        Example: "driving a Model 3" extracts "Model 3" as PRODUCT
        """
        escaped_terms = [re.escape(term) for term in terms]
        escaped_terms.sort(key=len, reverse=True)
        
        pattern_str = (
            f'{context_before}'
            f'({"|".join(escaped_terms)})'
            f'{context_after}'
        )
        
        return EntityPattern(
            entity_type=entity_type,
            pattern=re.compile(pattern_str, re.IGNORECASE),
            priority=priority
        )


def create_negation_patterns() -> List[re.Pattern]:
    """
    Create patterns to exclude false positives.
    E.g., "New York Times" should not extract "New York" as location in this context.
    """
    return [
        re.compile(r'\bNew\s+York\s+Times\b', re.IGNORECASE),
        re.compile(r'\bLos\s+Angeles\s+Times\b', re.IGNORECASE),
        re.compile(r'\bWall\s+Street\b', re.IGNORECASE),
        # Add more negation patterns as needed
    ]


def should_exclude_entity(text: str, start: int, end: int, negation_patterns: List[re.Pattern]) -> bool:
    """
    Check if an entity match should be excluded based on negation patterns.
    """
    # Check a window around the entity
    window_start = max(0, start - 20)
    window_end = min(len(text), end + 20)
    context = text[window_start:window_end]
    
    for pattern in negation_patterns:
        if pattern.search(context):
            return True
    
    return False
