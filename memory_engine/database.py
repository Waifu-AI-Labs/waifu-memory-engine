import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import os

DATABASE_PATH = os.getenv('DATABASE_PATH', 'waifu_memory.db')

def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    
    try:
        # Memory entries table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                character TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                emotion TEXT,
                importance REAL DEFAULT 0.5,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Personality traits table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS personality_traits (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                character TEXT NOT NULL,
                trait_name TEXT NOT NULL,
                trait_value REAL NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, character, trait_name)
            )
        ''')
        
        # Emotional states table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS emotional_states (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                character TEXT NOT NULL,
                emotion TEXT NOT NULL,
                intensity REAL NOT NULL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER DEFAULT 3600
            )
        ''')
        
        # User relationships table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                character TEXT NOT NULL,
                relationship_level REAL DEFAULT 0.5,
                trust_level REAL DEFAULT 0.5,
                affection_level REAL DEFAULT 0.5,
                interaction_count INTEGER DEFAULT 0,
                last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, character)
            )
        ''')
        
        # Events and milestones table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                character TEXT NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                importance REAL DEFAULT 0.5,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create indexes for better performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_memories_user_char ON memories(user_id, character)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_personality_user_char ON personality_traits(user_id, character)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_emotions_user_char ON emotional_states(user_id, character)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_emotions_timestamp ON emotional_states(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_user_char ON relationships(user_id, character)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_events_user_char ON events(user_id, character)')
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def cleanup_old_memories(retention_days=365):
    """Clean up old memories based on retention policy."""
    conn = get_db_connection()
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Only delete low-importance memories that haven't been accessed recently
        conn.execute('''
            DELETE FROM memories 
            WHERE timestamp < ? 
            AND importance < 0.3 
            AND access_count < 5
            AND last_accessed < ?
        ''', (cutoff_date, cutoff_date))
        
        conn.commit()
    except Exception as e:
        print(f"Error cleaning up memories: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
