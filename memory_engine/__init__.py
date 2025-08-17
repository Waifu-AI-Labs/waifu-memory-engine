"""
Waifu Memory Engine - Advanced memory management system for AI characters.

This package provides comprehensive memory storage, retrieval, and management
capabilities for creating persistent, emotionally intelligent AI characters.

Main Components:
- MemoryManager: Core memory storage and retrieval
- EmotionTracker: Emotional state tracking and analysis  
- PersonalityTracker: Personality trait management
- TextProcessor: NLP utilities for text processing
- Database functions: SQLite database management
"""

# Version information
__version__ = "1.0.0"
__author__ = "Waifu Memory Engine Team"

# Import main classes for convenient access
from .memory_manager import MemoryManager
from .emotion_tracker import EmotionTracker
from .personality import PersonalityTracker
from .utils import TextProcessor, calculate_memory_importance, extract_keywords, calculate_relevance_score
from .database import init_db, get_db_connection, cleanup_old_memories

# Define what gets imported with "from memory_engine import *"
__all__ = [
    'MemoryManager',
    'EmotionTracker', 
    'PersonalityTracker',
    'TextProcessor',
    'calculate_memory_importance',
    'extract_keywords',
    'calculate_relevance_score',
    'init_db',
    'get_db_connection',
    'cleanup_old_memories'
]
