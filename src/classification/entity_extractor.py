"""
Entity Extraction System
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Entity:
    """Represents an extracted entity"""
    type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int

class EntityExtractor:
    """Extracts entities from user queries"""

    def __init__(self):
        # Patterns for different entity types
        self.entity_patterns = {
            "order_number": [
                r'\bORD[\-\s]?\d{4}[\-\s]?\d{3,4}\b',  # ORD-XXXX-XXXX format (primary)
                r'\bORD[\-\s]?\d{4,8}\b',  # ORD-XXXX or ORDXXXX format (fallback)
            ],
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "phone": [
                r'\b(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                r'\b(\+44|0)[0-9\s]{10,11}\b'  # UK phone numbers
            ],
            "date": [
                r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',  # MM/DD/YYYY or DD/MM/YYYY
                r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY/MM/DD
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december|\d{1,2})(st|nd|rd|th)?\s+(\d{4}|\d{2})?\b'
            ],
            "amount": [
                r'\b\$?(\d+(?:\.\d{2})?)\b',  # Currency amounts
                r'\b(\d+(?:\.\d{2})?)\s*(dollars?|usd|eur|gbp)\b'
            ],
            "product_name": [
                r'\b(model|product|item)\s*[:\-]?\s*([A-Za-z0-9\s\-]{3,50})\b',
                r'\b(iPhone|iPad|MacBook|AirPods|Apple Watch|Samsung|Google|Pixel)\b',
                r'\b(size|color)\s*[:\-]?\s*([A-Za-z0-9\s\-]{2,30})\b'
            ],
            "tracking_number": [
                r'\b(tracking|track)\s*(number|#|id)?\s*[:\-]?\s*([A-Z0-9]{10,25})\b',
                r'\b(1Z[A-Z0-9]{16})\b',  # UPS format
                r'\b(9400\d{22})\b'  # USPS format
            ],
            "card_last_four": [
                r'\b(card|credit|debit)\s*(ending|last)?\s*(\d{4})\b',
                r'\b(\*\*\*\*|\*\*\*\*\s)\s*(\d{4})\b'
            ]
        }

        # Context keywords that help identify entities
        self.context_keywords = {
            "order_number": ["order", "purchase", "transaction", "ord", "#"],
            "email": ["email", "e-mail", "contact", "address"],
            "phone": ["phone", "mobile", "cell", "contact", "number"],
            "date": ["date", "when", "day", "time", "month", "year"],
            "amount": ["amount", "price", "cost", "total", "paid", "charge"],
            "product_name": ["product", "item", "model", "device", "phone", "laptop"],
            "tracking_number": ["tracking", "track", "package", "delivery", "shipping"],
            "card_last_four": ["card", "credit", "debit", "payment", "ending"]
        }

    def extract_entities(self, query: str) -> List[Entity]:
        """
        Extract entities from a query

        Args:
            query: User's query text

        Returns:
            List of extracted entities
        """
        entities = []
        query_lower = query.lower()

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(
                        entity_type, match.group(), query_lower
                    )

                    # Clean up the extracted value
                    value = self._clean_entity_value(entity_type, match.group())
                    
                    entity = Entity(
                        type=entity_type,
                        value=value,
                        confidence=confidence,
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities.append(entity)

        # Special handling for "order ORD-XXXX" patterns that weren't caught by direct patterns
        order_prefix_patterns = [
            r'\b(?:order|ord)\s+(?:#?\s*)?(ORD[\-\s]?\d+(?:[\-\s]?\d+)*)\b',
            r'\b(?:order|ord|#|no\.?|number)\s*[:\-]?\s*(ORD[\-\s]?\d+(?:[\-\s]?\d+)*)\b'
        ]
        
        for pattern in order_prefix_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                order_part = match.group(1)  # The captured ORD-XXXX part
                confidence = self._calculate_confidence(entity_type, order_part, query_lower)
                value = self._clean_entity_value(entity_type, order_part)
                
                entity = Entity(
                    type=entity_type,
                    value=value,
                    confidence=confidence,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                entities.append(entity)

        # Remove duplicates and sort by confidence
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.confidence, reverse=True)

        return entities

    def _calculate_confidence(self, entity_type: str, value: str, query_lower: str) -> float:
        """
        Calculate confidence score for an entity extraction

        Args:
            entity_type: Type of entity
            value: Extracted value
            query_lower: Lowercase query text

        Returns:
            Confidence score between 0 and 1
        """
        base_confidence = 0.7  # Base confidence for pattern match

        # Boost confidence if context keywords are present
        context_words = self.context_keywords.get(entity_type, [])
        context_boost = 0.0

        for word in context_words:
            if word in query_lower:
                context_boost += 0.1
                break  # Only boost once per entity type

        # Additional validation for specific entity types
        if entity_type == "order_number":
            # Order numbers should be reasonably long and alphanumeric
            if len(value) >= 6 and any(c.isdigit() for c in value):
                base_confidence += 0.1
            # Give highest confidence to ORD- prefixed orders
            if value.upper().startswith('ORD-'):
                base_confidence += 0.2
        elif entity_type == "email":
            # Email validation
            if '@' in value and '.' in value.split('@')[1]:
                base_confidence += 0.2
        elif entity_type == "phone":
            # Phone number validation (basic)
            digits_only = re.sub(r'\D', '', value)
            if 10 <= len(digits_only) <= 15:
                base_confidence += 0.1
        elif entity_type == "tracking_number":
            # Tracking numbers are usually long
            if len(value) >= 10:
                base_confidence += 0.1

        return min(base_confidence + context_boost, 1.0)

    def _clean_entity_value(self, entity_type: str, value: str) -> str:
        """
        Clean up extracted entity values

        Args:
            entity_type: Type of entity
            value: Raw extracted value

        Returns:
            Cleaned value
        """
        if entity_type == "order_number":
            # Normalize ORD- prefix and format
            value = value.upper().strip()
            
            # If it starts with ORD, normalize the format
            if value.startswith('ORD'):
                # Remove any existing hyphens after ORD
                value = re.sub(r'ORD[\-\s]*', 'ORD-', value)
                # Clean up any double hyphens or spaces
                value = re.sub(r'[\-\s]+', '-', value)
                return value
            
            # For other patterns, check if it looks like an order number and add ORD- prefix
            clean_value = re.sub(r'^(ORDER|ORD|#|NO\.?|NUMBER)\s*[:\-]?\s*', '', value, flags=re.IGNORECASE)
            
            # If the cleaned value looks like an order number, add ORD- prefix
            if re.match(r'^\d{4,8}$', clean_value) or re.match(r'^\d{4}[\-\s]?\d{3,4}$', clean_value):
                return f"ORD-{clean_value.replace('-', '').replace(' ', '')}"
            
            # Otherwise return as-is (might be a different format)
            return clean_value.upper()
        elif entity_type == "email":
            return value.lower().strip()
        elif entity_type == "phone":
            # Keep only digits, spaces, dashes, parentheses
            value = re.sub(r'[^\d\s\-\(\)\+]', '', value)
            return value.strip()
        elif entity_type == "amount":
            # Extract just the numeric part
            match = re.search(r'(\d+(?:\.\d{2})?)', value)
            return match.group(1) if match else value
        else:
            return value.strip()

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Remove duplicate entities, keeping the one with highest confidence and specificity

        Args:
            entities: List of entities

        Returns:
            Deduplicated list of entities
        """
        seen = {}
        for entity in entities:
            entity_type = entity.type
            entity_value = entity.value.lower()
            
            # For order numbers, check for substring relationships
            if entity_type == "order_number":
                # Check if this entity value is a substring of any existing entity
                should_skip = False
                for existing_key, existing_entity in seen.items():
                    if existing_key[0] == entity_type:  # Same type
                        existing_value = existing_key[1]
                        # If current value is substring of existing, skip it
                        if entity_value in existing_value and len(entity_value) < len(existing_value):
                            should_skip = True
                            break
                        # If existing value is substring of current, replace it
                        elif existing_value in entity_value and len(existing_value) < len(entity_value):
                            del seen[existing_key]
                            break
                
                if not should_skip:
                    key = (entity_type, entity_value)
                    seen[key] = entity
            else:
                # For other entity types, use existing logic
                key = (entity_type, entity_value)
                if key not in seen or entity.confidence > seen[key].confidence:
                    seen[key] = entity

        return list(seen.values())

    def get_entity_summary(self, entities: List[Entity]) -> Dict[str, Any]:
        """
        Get a summary of extracted entities

        Args:
            entities: List of entities

        Returns:
            Dictionary with entity counts and top entities
        """
        entity_counts = {}
        top_entities = {}

        for entity in entities:
            entity_type = entity.type
            if entity_type not in entity_counts:
                entity_counts[entity_type] = 0
                top_entities[entity_type] = entity
            entity_counts[entity_type] += 1

            # Keep the highest confidence entity for each type
            if entity.confidence > top_entities[entity_type].confidence:
                top_entities[entity_type] = entity

        return {
            "total_entities": len(entities),
            "entity_counts": entity_counts,
            "top_entities": {k: v.value for k, v in top_entities.items()},
            "entities": entities
        }

# Export singleton instance
entity_extractor = EntityExtractor()