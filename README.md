# 🧠 Waifu Memory Engine

An advanced memory system for anime waifu characters that provides persistent memory, personality learning, and emotional state tracking for integration with chat and voice synthesis systems.

## ✨ Features

- **🧠 Persistent Memory**: Long-term conversation history and context retention
- **👤 Personality Learning**: Adaptive personality traits based on user interactions
- **💭 Emotional State Tracking**: Maintains emotional context between sessions
- **📚 Knowledge Base**: Structured storage of facts, preferences, and relationships
- **🔗 Easy Integration**: RESTful API for seamless integration with existing waifu systems
- **🎯 Event Tracking**: Remembers important moments and milestones
- **🔍 Smart Retrieval**: Context-aware memory retrieval and relevance scoring

## 🧠 Academic Research

This project is backed by comprehensive research. Read our paper:
**[Waifu Memory Engine: A Context-Aware Memory System for Conversational AI Characters](RESEARCH_PAPER.md)**

> The Waifu Memory Engine presents a novel approach to persistent memory management in conversational AI systems, specifically designed for anime-style virtual characters (waifus). This system implements advanced memory storage, retrieval, and association mechanisms to enable AI characters to maintain coherent, long-term conversational context and develop consistent personalities through user interactions.

## 📚 Documentation

- **[📄 Research Paper](RESEARCH_PAPER.md)** - Complete technical paper on the memory engine architecture
- **[📖 API Documentation](API_DOCUMENTATION.md)** - Full API reference with examples
- **[🛠️ Technical Documentation](DOCUMENTATION.md)** - Detailed setup and usage guide
- **[🔬 Examples](examples/)** - Integration examples and demos

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- SQLite (included with Python)

### Installation

```bash
# Clone and navigate to the project
cd waifu-memory-engine

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -c "from memory_engine.database import init_db; init_db()"
```

### Run the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5002`

## 📚 API Documentation

### 💾 Store Memory
**POST** `/memory/store`

Store a new memory entry.

```json
{
    "user_id": "user123",
    "character": "sakura",
    "content": "User mentioned they love cherry blossoms",
    "memory_type": "preference",
    "emotion": "happy",
    "importance": 0.8
}
```

### 🔍 Retrieve Memories
**GET** `/memory/retrieve`

Retrieve relevant memories based on query.

```json
{
    "user_id": "user123",
    "character": "sakura", 
    "query": "flowers",
    "limit": 10
}
```

### 👤 Update Personality
**POST** `/personality/update`

Update character personality traits.

```json
{
    "user_id": "user123",
    "character": "sakura",
    "trait": "cheerfulness",
    "value": 0.9
}
```

### 💭 Set Emotional State
**POST** `/emotion/set`

Update current emotional state.

```json
{
    "user_id": "user123",
    "character": "sakura",
    "emotion": "excited",
    "intensity": 0.7,
    "context": "discussing favorite anime"
}
```

## 🎯 Integration Examples

### With Waifu Chat System

```python
import requests

def get_memory_context(user_id, message):
    # Retrieve relevant memories
    response = requests.get('http://localhost:5002/memory/retrieve', json={
        'user_id': user_id,
        'character': 'sakura',
        'query': message,
        'limit': 5
    })
    
    memories = response.json().get('memories', [])
    context = '\n'.join([mem['content'] for mem in memories])
    
    # Store new conversation
    requests.post('http://localhost:5002/memory/store', json={
        'user_id': user_id,
        'character': 'sakura',
        'content': f"User said: {message}",
        'memory_type': 'conversation',
        'emotion': 'neutral',
        'importance': 0.5
    })
    
    return context
```

### With Voice Synthesis

```python
def get_emotional_voice_params(user_id, character):
    response = requests.get(f'http://localhost:5002/emotion/current/{user_id}/{character}')
    emotion_data = response.json()
    
    # Map emotion to voice synthesis parameters
    emotion_mapping = {
        'happy': {'emotion': 'cheerful', 'pitch': '+10%'},
        'sad': {'emotion': 'sad', 'pitch': '-5%'},
        'excited': {'emotion': 'excited', 'rate': '+10%'}
    }
    
    return emotion_mapping.get(emotion_data.get('emotion'), {'emotion': 'neutral'})
```

## 🛠️ Development

### Project Structure

```
waifu-memory-engine/
├── app.py                    # Flask API server
├── memory_engine/
│   ├── __init__.py
│   ├── database.py           # Database models and operations
│   ├── memory_manager.py     # Core memory management
│   ├── personality.py        # Personality trait system
│   ├── emotion_tracker.py    # Emotional state management
│   └── utils.py              # Utility functions
├── config/
│   └── config.py             # Configuration settings
├── tests/
│   ├── test_memory.py
│   ├── test_personality.py
│   └── test_emotions.py
├── examples/
│   └── integration_demo.py   # Integration examples
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
└── README.md               # This documentation
```

### Memory Types

- **conversation**: General chat history
- **preference**: User likes/dislikes
- **fact**: Concrete information about user
- **event**: Important moments/milestones
- **relationship**: Information about relationships
- **personality**: Character trait adjustments

### Emotion System

The emotion system tracks:
- Current emotional state
- Emotional intensity (0.0 - 1.0)
- Emotional context and triggers
- Historical emotional patterns

## 📋 Requirements

- `flask>=2.3.3`
- `flask-cors>=4.0.0`
- `sqlite3` (built-in)
- `python-dotenv>=1.0.0`
- `datetime`
- `json`
- `uuid`

## 🔧 Configuration

Create a `.env` file:

```env
FLASK_PORT=5002
FLASK_DEBUG=True
DATABASE_PATH=waifu_memory.db
MAX_MEMORIES_PER_QUERY=50
MEMORY_RETENTION_DAYS=365
```

## 🤝 Integration with Existing Systems

### Waifu Chat Integration

The memory engine can enhance your chat system by:
- Providing conversation context
- Remembering user preferences
- Maintaining personality consistency
- Tracking relationship progression

### Voice Synthesis Integration

Enhance voice responses with:
- Emotion-appropriate voice parameters
- Context-aware tone adjustments
- Personality-driven speech patterns

## 📄 License

MIT License - Perfect for your waifu ecosystem! 🌸

## 🙏 Acknowledgments

Built to complement the Waifu-AI-Labs ecosystem:
- waifu-chat-ollama
- waifu-voice-synthesis

Made with ❤️ for the waifu community
