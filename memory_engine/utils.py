"""
Utility functions for the Waifu Memory Engine
"""
import re
import math
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    import nltk
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)

class TextProcessor:
    """Text processing utilities for memory content analysis."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.lower()
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        # Clean and tokenize
        clean_text = self.clean_text(text)
        words = word_tokenize(clean_text)
        
        # Remove stop words and short words
        keywords = [
            self.stemmer.stem(word) 
            for word in words 
            if word not in self.stop_words 
            and len(word) > 2
            and word.isalpha()
        ]
        
        # Count and return most common
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using keyword overlap."""
        if not text1 or not text2:
            return 0.0
        
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Jaccard similarity
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0

def calculate_relevance_score(content: str, query: str) -> float:
    """Calculate relevance score between content and query."""
    processor = TextProcessor()
    return processor.calculate_similarity(content, query)

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text."""
    processor = TextProcessor()
    return processor.extract_keywords(text, max_keywords)

def calculate_memory_importance(
    content: str,
    memory_type: str,
    emotional_weight: float = 0.0,
    user_interaction: bool = False,
    keywords: List[str] = None
) -> float:
    """Calculate importance score for a memory."""
    base_importance = {
        'conversation': 0.3,
        'event': 0.6,
        'preference': 0.8,
        'fact': 0.5,
        'relationship': 0.9,
        'milestone': 0.95
    }.get(memory_type, 0.4)
    
    # Adjust based on content length (longer might be more important)
    content_factor = min(1.0, len(content) / 200) * 0.1
    
    # Adjust based on emotional weight
    emotion_factor = abs(emotional_weight) * 0.2
    
    # Adjust if user directly interacted
    interaction_factor = 0.1 if user_interaction else 0.0
    
    # Adjust based on keyword richness
    keyword_factor = 0.0
    if keywords:
        keyword_factor = min(0.15, len(keywords) / 20)  # More keywords = more important
    
    importance = base_importance + content_factor + emotion_factor + interaction_factor + keyword_factor
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, importance))

def calculate_emotion_intensity(
    current_emotion: str,
    new_emotion: str,
    current_intensity: float,
    time_since_last: timedelta
) -> float:
    """Calculate new emotion intensity based on current state and time decay."""
    # Emotion compatibility matrix (how emotions reinforce or dampen each other)
    emotion_compatibility = {
        ('happy', 'excited'): 1.2,
        ('happy', 'content'): 1.1,
        ('sad', 'angry'): 0.8,
        ('angry', 'frustrated'): 1.3,
        ('surprised', 'curious'): 1.1,
        ('fearful', 'anxious'): 1.2,
    }
    
    # Base decay rate (emotions fade over time)
    decay_rate = 0.1  # per hour
    hours_passed = time_since_last.total_seconds() / 3600
    
    # Apply time decay to current intensity
    decayed_intensity = current_intensity * math.exp(-decay_rate * hours_passed)
    
    # Check if emotions are compatible
    compatibility = emotion_compatibility.get((current_emotion, new_emotion), 1.0)
    compatibility = compatibility if current_emotion != new_emotion else 0.9  # Same emotion slightly dampens
    
    # Calculate new intensity
    base_new_intensity = 0.5  # Default intensity for new emotions
    combined_intensity = (decayed_intensity * 0.3) + (base_new_intensity * 0.7 * compatibility)
    
    return max(0.0, min(1.0, combined_intensity))

def generate_memory_hash(content: str, user_id: str, character: str) -> str:
    """Generate a hash for memory deduplication."""
    combined = f"{user_id}:{character}:{content.strip().lower()}"
    return hashlib.md5(combined.encode()).hexdigest()

def format_timestamp(dt: datetime) -> str:
    """Format datetime for consistent display."""
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string back to datetime."""
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S UTC')
    except ValueError:
        try:
            # Try ISO format as fallback
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return None

def validate_memory_content(content: str, memory_type: str) -> Tuple[bool, str]:
    """Validate memory content based on type."""
    if not content or not content.strip():
        return False, "Content cannot be empty"
    
    content = content.strip()
    
    # Type-specific validation
    max_lengths = {
        'conversation': 1000,
        'event': 500,
        'preference': 200,
        'fact': 300,
        'relationship': 400,
        'milestone': 500
    }
    
    max_length = max_lengths.get(memory_type, 500)
    if len(content) > max_length:
        return False, f"Content too long for type '{memory_type}' (max {max_length} characters)"
    
    # Basic content quality checks
    if len(content) < 3:
        return False, "Content too short"
    
    # Check for obvious spam patterns
    if content.count('!') > 10 or content.count('?') > 10:
        return False, "Content appears to be spam"
    
    return True, "Content is valid"

def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent issues."""
    if not text:
        return ""
    
    # Remove potential harmful characters
    text = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Limit length
    return text[:2000]  # Max 2000 characters

def calculate_time_weight(timestamp: datetime, current_time: datetime = None) -> float:
    """Calculate time-based weight for memories (more recent = higher weight)."""
    if current_time is None:
        current_time = datetime.utcnow()
    
    time_diff = current_time - timestamp
    days_old = time_diff.total_seconds() / (24 * 3600)
    
    # Exponential decay with half-life of 30 days
    half_life = 30.0
    weight = math.exp(-math.log(2) * days_old / half_life)
    
    return max(0.01, min(1.0, weight))  # Keep minimum weight of 0.01

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text (basic implementation)."""
    # This is a simple implementation - in production you might want to use spaCy or similar
    entities = {
        'names': [],
        'places': [],
        'dates': [],
        'numbers': []
    }
    
    # Simple regex patterns for basic entity extraction
    name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b'
    number_pattern = r'\b\d+\b'
    
    entities['names'] = re.findall(name_pattern, text)
    entities['dates'] = re.findall(date_pattern, text)
    entities['numbers'] = re.findall(number_pattern, text)
    
    return entities

def create_response_context(
    memories: List[Dict],
    current_emotion: Dict,
    user_id: str,
    character: str
) -> Dict[str, Any]:
    """Create context object for response generation."""
    context = {
        'user_id': user_id,
        'character': character,
        'timestamp': datetime.utcnow().isoformat(),
        'recent_memories': [],
        'important_memories': [],
        'emotional_state': current_emotion,
        'conversation_themes': [],
        'relationship_duration': None
    }
    
    if memories:
        # Sort memories by recency and importance
        sorted_memories = sorted(
            memories,
            key=lambda x: (x.get('importance', 0) * 0.6 + 
                          calculate_time_weight(parse_timestamp(x.get('timestamp', ''))) * 0.4),
            reverse=True
        )
        
        context['recent_memories'] = sorted_memories[:5]
        context['important_memories'] = [
            m for m in sorted_memories if m.get('importance', 0) > 0.7
        ][:3]
        
        # Extract common themes
        all_content = ' '.join([m.get('content', '') for m in memories])
        context['conversation_themes'] = extract_keywords(all_content, 5)
    
    return context
