# 📡 Waifu Memory Engine API Documentation

**Base URL:** `http://localhost:5003`  
**Content-Type:** `application/json`  
**API Version:** v1.0

## 📋 Table of Contents

- [Health Check](#health-check)
- [Memory Management](#memory-management)
- [Emotion Tracking](#emotion-tracking)
- [Integration Endpoints](#integration-endpoints)
- [Text Analysis](#text-analysis)
- [Administration](#administration)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## 🏥 Health Check

### GET /health
Check API server health and status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-17T12:44:43.322695",
  "service": "waifu-memory-engine"
}
```

---

## 🧠 Memory Management

### POST /memory/store
Store a new memory entry in the database.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)", 
  "content": "string (required)",
  "memory_type": "string (required)",
  "emotion": "string (optional)",
  "importance": "float (optional, auto-calculated if not provided)",
  "emotion_intensity": "float (optional, 0.0-1.0)",
  "metadata": "object (optional)"
}
```

**Memory Types:**
- `conversation` - Chat interactions
- `preference` - User preferences 
- `event` - Significant events
- `fact` - Factual information
- `relationship` - Relationship milestones
- `milestone` - Important achievements

**Response:**
```json
{
  "success": true,
  "memory_id": "uuid",
  "message": "Memory stored successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5003/memory/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "character": "sakura_ai",
    "content": "User loves chocolate ice cream and cats",
    "memory_type": "preference",
    "importance": 0.8
  }'
```

---

### POST /memory/retrieve
Retrieve memories based on query and filters.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "query": "string (optional)",
  "memory_type": "string (optional)",
  "limit": "integer (optional, default: 10)",
  "min_importance": "float (optional, default: 0.0)"
}
```

**Response:**
```json
{
  "success": true,
  "memories": [
    {
      "id": "uuid",
      "user_id": "string",
      "character": "string", 
      "content": "string",
      "memory_type": "string",
      "emotion": "string",
      "importance": "float",
      "timestamp": "datetime",
      "last_accessed": "datetime",
      "access_count": "integer",
      "metadata": "object"
    }
  ],
  "total_count": "integer"
}
```

**Example:**
```bash
curl -X POST http://localhost:5003/memory/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "character": "sakura_ai",
    "query": "ice cream",
    "memory_type": "preference",
    "limit": 5
  }'
```

---

### POST /memory/summary
Get memory activity summary for a user-character pair.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "days": "integer (optional, default: 30)"
}
```

**Response:**
```json
{
  "success": true,
  "memory_stats": [
    {
      "memory_type": "string",
      "count": "integer",
      "avg_importance": "float"
    }
  ],
  "important_memories": [
    {
      "content": "string",
      "importance": "float", 
      "timestamp": "datetime",
      "memory_type": "string"
    }
  ],
  "period_days": "integer"
}
```

---

### POST /memory/preferences
Get all user preferences organized by categories.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "limit": "integer (optional, default: 100)",
  "min_importance": "float (optional, default: 0.0)"
}
```

**Response:**
```json
{
  "success": true,
  "preferences": {
    "all": ["array of all preference memories"],
    "categorized": {
      "food": ["food-related preferences"],
      "activities": ["activity preferences"],
      "personality": ["personality preferences"],
      "relationships": ["relationship preferences"],
      "other": ["uncategorized preferences"]
    },
    "total_count": "integer"
  }
}
```

---

## 💭 Emotion Tracking

### POST /emotion/update
Update the character's emotional state.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "emotion": "string (required)",
  "intensity": "float (optional, default: 0.5, range: 0.0-1.0)",
  "trigger": "string (optional)"
}
```

**Supported Emotions:**
- `happy`, `sad`, `angry`, `surprised`, `disgusted`, `fearful`, `neutral`
- `excited`, `confused`, `content`, `playful`, `affectionate`, `curious`, `shy`, `proud`

**Response:**
```json
{
  "success": true,
  "message": "Emotion updated successfully",
  "emotion_state": {
    "primary_emotion": "string",
    "intensity": "float",
    "timestamp": "datetime"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5003/emotion/update \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "character": "sakura_ai",
    "emotion": "happy",
    "intensity": 0.8,
    "trigger": "User complimented my cooking"
  }'
```

---

### POST /emotion/current
Get the current emotional state of a character.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "emotion_state": {
    "primary_emotion": "string",
    "intensity": "float",
    "last_updated": "datetime",
    "duration": "seconds",
    "trigger": "string"
  }
}
```

---

### POST /emotion/history
Get emotion history for a character over a specified period.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "days": "integer (optional, default: 7)"
}
```

**Response:**
```json
{
  "success": true,
  "emotion_history": [
    {
      "emotion": "string",
      "intensity": "float",
      "timestamp": "datetime",
      "trigger": "string",
      "duration_minutes": "integer"
    }
  ],
  "summary": {
    "most_common_emotion": "string",
    "avg_intensity": "float",
    "total_changes": "integer"
  }
}
```

---

## 🔗 Integration Endpoints

### POST /integration/context
Get comprehensive conversation context for chat system integration.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "context": {
    "recent_memories": ["array of recent conversation memories"],
    "current_emotion": {
      "primary_emotion": "string",
      "intensity": "float",
      "last_updated": "datetime"
    },
    "memory_summary": [
      {
        "memory_type": "string",
        "count": "integer",
        "avg_importance": "float"
      }
    ],
    "timestamp": "datetime"
  }
}
```

**Usage Example:**
```python
# In your chat system
context = get_conversation_context(user_id, character)
enhanced_prompt = f"""
Respond as {character} to: {user_message}

Recent context: {context['recent_memories']}
Current emotion: {context['current_emotion']['primary_emotion']}
Emotional intensity: {context['current_emotion']['intensity']}
"""
```

---

### POST /integration/process_conversation
Process a complete conversation turn and store memories automatically.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "character": "string (required)",
  "user_message": "string (required)",
  "character_response": "string (required)",
  "detected_emotion": "string (optional)",
  "emotion_intensity": "float (optional)",
  "importance": "float (optional, default: 0.4)",
  "turn_id": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation processed successfully",
  "results": [
    {
      "success": true,
      "memory_id": "uuid",
      "message": "Memory stored successfully"
    }
  ]
}
```

**Usage Example:**
```python
# After generating a chat response
process_conversation({
  "user_id": "user123",
  "character": "sakura_ai", 
  "user_message": "How are you feeling today?",
  "character_response": "I'm feeling quite happy! Thank you for asking.",
  "detected_emotion": "happy",
  "emotion_intensity": 0.7
})
```

---

## 🔍 Text Analysis

### POST /analysis/keywords
Extract keywords from text using NLP processing.

**Request Body:**
```json
{
  "text": "string (required)",
  "max_keywords": "integer (optional, default: 10)"
}
```

**Response:**
```json
{
  "success": true,
  "keywords": ["array", "of", "extracted", "keywords"],
  "cleaned_text": "normalized and cleaned text",
  "word_count": "integer"
}
```

**Example:**
```bash
curl -X POST http://localhost:5003/analysis/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I really love eating chocolate ice cream while watching anime!",
    "max_keywords": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "keywords": ["love", "eat", "chocol", "ice", "cream"],
  "cleaned_text": "really love eating chocolate ice cream while watching anime",
  "word_count": 9
}
```

---

## ⚙️ Administration

### POST /admin/cleanup
Schedule cleanup of old, low-importance memories.

**Request Body:**
```json
{
  "days_old": "integer (optional, default: 90)",
  "min_importance": "float (optional, default: 0.3)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cleanup scheduled for memories older than 90 days with importance < 0.3"
}
```

---

## ❌ Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": "Error message description"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing required fields, invalid data)
- `500` - Internal Server Error

### Common Errors
- **Missing required field**: `"Missing required field: user_id"`
- **Invalid memory type**: `"Invalid memory_type. Must be one of: conversation, preference, event, fact, relationship, milestone"`
- **Database error**: `"Database connection failed"`
- **Invalid emotion**: `"Unsupported emotion type"`

---

## 📚 Complete Usage Examples

### Basic Memory Storage and Retrieval
```python
import requests

api_base = "http://localhost:5003"

# Store a preference
response = requests.post(f"{api_base}/memory/store", json={
    "user_id": "alice",
    "character": "sakura",
    "content": "User loves cats and enjoys reading manga",
    "memory_type": "preference",
    "importance": 0.8
})
print(response.json())

# Retrieve preferences
response = requests.post(f"{api_base}/memory/preferences", json={
    "user_id": "alice", 
    "character": "sakura"
})
preferences = response.json()
print(f"Found {preferences['preferences']['total_count']} preferences")
```

### Emotion Tracking Workflow
```python
# Update emotion
requests.post(f"{api_base}/emotion/update", json={
    "user_id": "alice",
    "character": "sakura", 
    "emotion": "excited",
    "intensity": 0.9,
    "trigger": "User mentioned going to a cat cafe"
})

# Get current emotion for voice synthesis
response = requests.post(f"{api_base}/emotion/current", json={
    "user_id": "alice",
    "character": "sakura"
})
emotion = response.json()['emotion_state']

# Use emotion for voice parameters
voice_params = {
    'speed': 1.2 if emotion['primary_emotion'] == 'excited' else 1.0,
    'pitch': 0.1 * emotion['intensity'],
    'volume': 1.0 + (0.1 * emotion['intensity'])
}
```

### Chat System Integration
```python
def enhanced_chat_response(user_id, character, user_message):
    # Get context
    context_response = requests.post(f"{api_base}/integration/context", json={
        "user_id": user_id,
        "character": character
    })
    context = context_response.json()['context']
    
    # Generate response using your chat system
    # (integrate with your waifu-chat-ollama here)
    character_response = generate_response_with_context(user_message, context)
    
    # Process and store the conversation
    requests.post(f"{api_base}/integration/process_conversation", json={
        "user_id": user_id,
        "character": character,
        "user_message": user_message,
        "character_response": character_response,
        "detected_emotion": detect_emotion(user_message)  # Your emotion detection
    })
    
    return character_response
```

### Batch Memory Analysis
```python
# Get all memories for analysis
response = requests.post(f"{api_base}/memory/retrieve", json={
    "user_id": "alice",
    "character": "sakura", 
    "limit": 1000
})

memories = response.json()['memories']

# Analyze conversation patterns
conversation_memories = [m for m in memories if m['memory_type'] == 'conversation']
preference_memories = [m for m in memories if m['memory_type'] == 'preference']

print(f"Total conversations: {len(conversation_memories)}")
print(f"Total preferences: {len(preference_memories)}")

# Extract keywords from all content
all_content = ' '.join([m['content'] for m in memories])
response = requests.post(f"{api_base}/analysis/keywords", json={
    "text": all_content,
    "max_keywords": 20
})
print("Most common topics:", response.json()['keywords'])
```

---

## 🔧 Integration Patterns

### Pattern 1: Real-time Chat Enhancement
```python
def chat_with_memory(user_id, character, message):
    # 1. Get context
    context = get_context(user_id, character)
    
    # 2. Generate response with context
    response = your_chat_system.generate(message, context)
    
    # 3. Store conversation
    process_conversation(user_id, character, message, response)
    
    return response
```

### Pattern 2: Emotion-Aware Voice Synthesis
```python
def speak_with_emotion(user_id, character, text):
    # 1. Get current emotion
    emotion = get_current_emotion(user_id, character)
    
    # 2. Adjust voice parameters
    voice_params = emotion_to_voice_params(emotion)
    
    # 3. Generate speech
    audio = your_voice_system.synthesize(text, voice_params)
    
    return audio
```

### Pattern 3: Preference-Based Responses
```python
def personalized_response(user_id, character, query):
    # 1. Get relevant preferences
    prefs = get_user_preferences(user_id, character)
    
    # 2. Filter preferences by relevance to query
    relevant_prefs = find_relevant_preferences(prefs, query)
    
    # 3. Generate personalized response
    response = generate_with_preferences(query, relevant_prefs)
    
    return response
```

---

**🚀 Ready to integrate?** Your waifu memory engine provides all the APIs needed to create engaging, memory-enhanced AI character experiences!
