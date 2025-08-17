"""
Configuration settings for the Waifu Memory Engine
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Database Configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'waifu_memory.db')
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Memory Engine Configuration
    MEMORY_CONFIG = {
        'max_memories_per_user': 10000,
        'memory_cleanup_threshold': 90,  # days
        'min_importance_threshold': 0.1,
        'max_daily_memories': 500,
        'importance_decay_rate': 0.01,  # daily decay for unused memories
        'association_strength_threshold': 0.3,
    }
    
    # Emotion Tracking Configuration
    EMOTION_CONFIG = {
        'emotion_decay_rate': 0.1,  # how fast emotions fade
        'max_emotion_history': 1000,
        'emotion_intensity_levels': {
            'very_low': 0.1,
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7,
            'very_high': 0.9
        },
        'base_emotions': [
            'happy', 'sad', 'angry', 'surprised', 'disgusted', 
            'fearful', 'neutral', 'excited', 'confused', 'content',
            'playful', 'affectionate', 'curious', 'shy', 'proud'
        ]
    }
    
    # Memory Types Configuration
    MEMORY_TYPES = {
        'conversation': {
            'default_importance': 0.4,
            'max_content_length': 1000,
            'retention_days': 180
        },
        'event': {
            'default_importance': 0.7,
            'max_content_length': 500,
            'retention_days': 365
        },
        'preference': {
            'default_importance': 0.8,
            'max_content_length': 200,
            'retention_days': 730
        },
        'fact': {
            'default_importance': 0.6,
            'max_content_length': 300,
            'retention_days': 365
        },
        'relationship': {
            'default_importance': 0.9,
            'max_content_length': 400,
            'retention_days': 1095  # 3 years
        },
        'milestone': {
            'default_importance': 0.95,
            'max_content_length': 500,
            'retention_days': -1  # never delete
        }
    }
    
    # API Configuration
    API_CONFIG = {
        'rate_limit': '1000 per hour',
        'cors_origins': ['http://localhost:3000', 'http://localhost:5001', 'http://localhost:5002'],
        'request_timeout': 30,
        'max_request_size': '10mb'
    }
    
    # Integration Configuration (for your chat and voice systems)
    INTEGRATION_CONFIG = {
        'chat_api_url': os.environ.get('CHAT_API_URL', 'http://localhost:5001'),
        'voice_api_url': os.environ.get('VOICE_API_URL', 'http://localhost:5002'),
        'personality_api_url': os.environ.get('PERSONALITY_API_URL', 'http://localhost:5004'),  # for future personality engine
        'webhook_secret': os.environ.get('WEBHOOK_SECRET', 'memory-engine-webhook-secret'),
        'enable_cross_system_sync': True
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': os.environ.get('LOG_FILE', 'memory_engine.log'),
        'max_bytes': 10485760,  # 10MB
        'backup_count': 5
    }

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    DATABASE_PATH = 'dev_waifu_memory.db'

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/waifu_memory.db')
    
    # Production-specific settings
    MEMORY_CONFIG = Config.MEMORY_CONFIG.copy()
    MEMORY_CONFIG.update({
        'max_memories_per_user': 50000,
        'memory_cleanup_threshold': 180,  # days
        'max_daily_memories': 1000,
    })

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory database for tests

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Get configuration class based on environment."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig)
