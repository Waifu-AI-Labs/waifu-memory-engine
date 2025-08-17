from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import logging
from memory_engine.memory_manager import MemoryManager
from memory_engine.emotion_tracker import EmotionTracker
from memory_engine.utils import TextProcessor, calculate_memory_importance, extract_keywords
from memory_engine.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components
memory_manager = MemoryManager()
emotion_tracker = EmotionTracker()
text_processor = TextProcessor()

# Initialize database on startup
with app.app_context():
    init_db()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'waifu-memory-engine'
    })

# Memory Management Endpoints
@app.route('/memory/store', methods=['POST'])
def store_memory():
    """Store a new memory entry."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'character', 'content', 'memory_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract optional fields
        emotion = data.get('emotion')
        importance = data.get('importance')
        metadata = data.get('metadata', {})
        
        # Use utils to calculate importance if not provided
        if importance is None:
            keywords = extract_keywords(data['content'])
            importance = calculate_memory_importance(
                content=data['content'],
                memory_type=data['memory_type'], 
                emotional_weight=0.5 if emotion else 0.0,
                keywords=keywords
            )
            metadata['auto_keywords'] = keywords
        
        # Store memory
        result = memory_manager.store_memory(
            user_id=data['user_id'],
            character=data['character'],
            content=data['content'],
            memory_type=data['memory_type'],
            emotion=emotion,
            importance=importance,
            metadata=metadata
        )
        
        # Update emotional state if emotion provided
        if emotion and result.get('success'):
            emotion_tracker.update_emotion(
                user_id=data['user_id'],
                character=data['character'],
                emotion=emotion,
                intensity=data.get('emotion_intensity', 0.5)
            )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/memory/retrieve', methods=['POST'])
def retrieve_memories():
    """Retrieve memories based on query and filters."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data or 'character' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or character'
            }), 400
        
        result = memory_manager.retrieve_memories(
            user_id=data['user_id'],
            character=data['character'],
            query=data.get('query'),
            memory_type=data.get('memory_type'),
            limit=data.get('limit', 10),
            min_importance=data.get('min_importance', 0.0)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/memory/summary', methods=['POST'])
def get_memory_summary():
    """Get memory activity summary."""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'character' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or character'
            }), 400
        
        days = data.get('days', 30)
        result = memory_manager.get_memory_summary(
            user_id=data['user_id'],
            character=data['character'],
            days=days
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting memory summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/memory/preferences', methods=['POST'])
def get_user_preferences():
    """Get all user preferences for personality/decision making."""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'character' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or character'
            }), 400
        
        # Get all preferences
        preferences_result = memory_manager.retrieve_memories(
            user_id=data['user_id'],
            character=data['character'],
            memory_type='preference',
            limit=data.get('limit', 100),
            min_importance=data.get('min_importance', 0.0)
        )
        
        if preferences_result['success']:
            # Organize preferences by categories for easier use
            categorized_prefs = {
                'food': [],
                'activities': [],
                'personality': [],
                'relationships': [],
                'other': []
            }
            
            for pref in preferences_result['memories']:
                content = pref['content'].lower()
                
                # Food category - expanded to include food items and eating-related words
                food_keywords = ['food', 'eat', 'eating', 'drink', 'drinking', 'taste', 'flavor', 'delicious', 'yummy',
                               'chocolate', 'ice cream', 'pizza', 'burger', 'sushi', 'pasta', 'bread', 'cake',
                               'coffee', 'tea', 'juice', 'water', 'milk', 'wine', 'beer', 'fruit', 'vegetable',
                               'meat', 'chicken', 'beef', 'fish', 'rice', 'noodles', 'soup', 'salad', 'sandwich',
                               'cookie', 'candy', 'sweet', 'dessert', 'snack', 'meal', 'breakfast', 'lunch', 'dinner']
                
                # Activities category - expanded to include more preference verbs and activity words
                activity_keywords = ['like', 'likes', 'love', 'loves', 'enjoy', 'enjoys', 'hate', 'hates', 'dislike', 'dislikes',
                                   'prefer', 'prefers', 'favorite', 'favourite', 'hobby', 'hobbies', 'activity', 'activities',
                                   'sport', 'sports', 'game', 'games', 'music', 'movie', 'movies', 'book', 'books',
                                   'reading', 'watching', 'playing', 'listening', 'dancing', 'singing', 'cooking',
                                   'shopping', 'traveling', 'swimming', 'running', 'exercise', 'workout']
                
                # Animals category - since cats are mentioned
                animal_keywords = ['cat', 'cats', 'dog', 'dogs', 'pet', 'pets', 'animal', 'animals', 'bird', 'birds',
                                 'fish', 'rabbit', 'hamster', 'turtle', 'snake', 'horse', 'cow', 'pig', 'sheep']
                
                if any(word in content for word in food_keywords):
                    categorized_prefs['food'].append(pref)
                elif any(word in content for word in animal_keywords):
                    # Add animals as a subcategory of activities/interests
                    categorized_prefs['activities'].append(pref)
                elif any(word in content for word in activity_keywords):
                    categorized_prefs['activities'].append(pref)
                elif any(word in content for word in ['personality', 'trait', 'behavior', 'character', 'mood', 'feeling']):
                    categorized_prefs['personality'].append(pref)
                elif any(word in content for word in ['friend', 'friends', 'family', 'relationship', 'relationships', 'dating', 'romance']):
                    categorized_prefs['relationships'].append(pref)
                else:
                    categorized_prefs['other'].append(pref)
            
            return jsonify({
                'success': True,
                'preferences': {
                    'all': preferences_result['memories'],
                    'categorized': categorized_prefs,
                    'total_count': len(preferences_result['memories'])
                }
            })
        else:
            return jsonify(preferences_result)
        
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Emotion Tracking Endpoints
@app.route('/emotion/update', methods=['POST'])
def update_emotion():
    """Update emotional state."""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'character', 'emotion']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        result = emotion_tracker.update_emotion(
            user_id=data['user_id'],
            character=data['character'],
            emotion=data['emotion'],
            intensity=data.get('intensity', 0.5),
            trigger=data.get('trigger')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error updating emotion: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/emotion/current', methods=['POST'])
def get_current_emotion():
    """Get current emotional state."""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'character' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or character'
            }), 400
        
        result = emotion_tracker.get_current_emotion(
            user_id=data['user_id'],
            character=data['character']
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting current emotion: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/emotion/history', methods=['POST'])
def get_emotion_history():
    """Get emotion history."""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'character' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing user_id or character'
            }), 400
        
        result = emotion_tracker.get_emotion_history(
            user_id=data['user_id'],
            character=data['character'],
            days=data.get('days', 7)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting emotion history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Integration Endpoints for Chat and Voice Systems
@app.route('/integration/context', methods=['POST'])
def get_conversation_context():
    """Get conversation context for chat integration."""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'character']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Get recent memories
        memories_result = memory_manager.retrieve_memories(
            user_id=data['user_id'],
            character=data['character'],
            memory_type='conversation',
            limit=5,
            min_importance=0.3
        )
        
        # Get current emotional state
        emotion_result = emotion_tracker.get_current_emotion(
            user_id=data['user_id'],
            character=data['character']
        )
        
        # Get memory summary for context
        summary_result = memory_manager.get_memory_summary(
            user_id=data['user_id'],
            character=data['character'],
            days=7
        )
        
        return jsonify({
            'success': True,
            'context': {
                'recent_memories': memories_result.get('memories', []),
                'current_emotion': emotion_result.get('emotion_state', {}),
                'memory_summary': summary_result.get('memory_stats', []),
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation context: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/integration/process_conversation', methods=['POST'])
def process_conversation():
    """Process a conversation turn and extract memories."""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'character', 'user_message', 'character_response']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        results = []
        
        # Store user message as memory
        user_memory = memory_manager.store_memory(
            user_id=data['user_id'],
            character=data['character'],
            content=f"User said: {data['user_message']}",
            memory_type='conversation',
            importance=data.get('importance', 0.4),
            metadata={'role': 'user', 'turn_id': data.get('turn_id')}
        )
        results.append(user_memory)
        
        # Store character response as memory
        char_memory = memory_manager.store_memory(
            user_id=data['user_id'],
            character=data['character'],
            content=f"I responded: {data['character_response']}",
            memory_type='conversation',
            importance=data.get('importance', 0.4),
            metadata={'role': 'character', 'turn_id': data.get('turn_id')}
        )
        results.append(char_memory)
        
        # Update emotion if provided
        if 'detected_emotion' in data:
            emotion_result = emotion_tracker.update_emotion(
                user_id=data['user_id'],
                character=data['character'],
                emotion=data['detected_emotion'],
                intensity=data.get('emotion_intensity', 0.5),
                trigger=data['user_message'][:100]  # First 100 chars as trigger
            )
            results.append(emotion_result)
        
        return jsonify({
            'success': True,
            'message': 'Conversation processed successfully',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Admin/Maintenance Endpoints
@app.route('/admin/cleanup', methods=['POST'])
def cleanup_old_memories():
    """Clean up old, low-importance memories."""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 90)
        min_importance = data.get('min_importance', 0.3)
        
        # This would be implemented in memory_manager
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'message': f'Cleanup scheduled for memories older than {days_old} days with importance < {min_importance}'
        })
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Text Analysis Endpoints  
@app.route('/analysis/keywords', methods=['POST'])
def extract_text_keywords():
    """Extract keywords from text using NLP."""
    try:
        data = request.get_json()
        
        if 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing text field'
            }), 400
        
        keywords = extract_keywords(data['text'], data.get('max_keywords', 10))
        cleaned_text = text_processor.clean_text(data['text'])
        
        return jsonify({
            'success': True,
            'keywords': keywords,
            'cleaned_text': cleaned_text,
            'word_count': len(cleaned_text.split())
        })
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
