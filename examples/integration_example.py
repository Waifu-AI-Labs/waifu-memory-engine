"""
Example integration script showing how to connect the Memory Engine
with the Chat and Voice systems from your other repositories.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class WaifuMemoryIntegration:
    """Integration client for connecting memory engine with chat and voice systems."""
    
    def __init__(self, 
                 memory_api_url: str = "http://localhost:5003",
                 chat_api_url: str = "http://localhost:5001", 
                 voice_api_url: str = "http://localhost:5002"):
        self.memory_api = memory_api_url
        self.chat_api = chat_api_url
        self.voice_api = voice_api_url
    
    # Memory Engine Integration Methods
    
    def store_conversation_memory(self, user_id: str, character: str, 
                                user_message: str, character_response: str,
                                emotion: str = None, importance: float = 0.4) -> Dict:
        """Store a conversation turn in memory."""
        return requests.post(f"{self.memory_api}/integration/process_conversation", 
                           json={
                               'user_id': user_id,
                               'character': character,
                               'user_message': user_message,
                               'character_response': character_response,
                               'detected_emotion': emotion,
                               'importance': importance,
                               'turn_id': f"turn_{datetime.now().timestamp()}"
                           }).json()
    
    def get_conversation_context(self, user_id: str, character: str) -> Dict:
        """Get memory context for enhancing chat responses."""
        response = requests.post(f"{self.memory_api}/integration/context",
                               json={'user_id': user_id, 'character': character})
        return response.json().get('context', {})
    
    def store_user_preference(self, user_id: str, character: str, 
                            preference: str, importance: float = 0.8) -> Dict:
        """Store a user preference."""
        return requests.post(f"{self.memory_api}/memory/store", json={
            'user_id': user_id,
            'character': character,
            'content': preference,
            'memory_type': 'preference',
            'importance': importance
        }).json()
    
    def store_relationship_milestone(self, user_id: str, character: str, 
                                   milestone: str) -> Dict:
        """Store an important relationship milestone."""
        return requests.post(f"{self.memory_api}/memory/store", json={
            'user_id': user_id,
            'character': character,
            'content': milestone,
            'memory_type': 'milestone',
            'importance': 0.95
        }).json()
    
    def update_emotion(self, user_id: str, character: str, emotion: str, 
                      intensity: float = 0.5, trigger: str = None) -> Dict:
        """Update character's emotional state."""
        return requests.post(f"{self.memory_api}/emotion/update", json={
            'user_id': user_id,
            'character': character,
            'emotion': emotion,
            'intensity': intensity,
            'trigger': trigger
        }).json()
    
    def get_current_emotion(self, user_id: str, character: str) -> Dict:
        """Get current emotional state for voice synthesis."""
        response = requests.post(f"{self.memory_api}/emotion/current",
                               json={'user_id': user_id, 'character': character})
        return response.json().get('emotion_state', {})
    
    # Integration with Chat System (waifu-chat-ollama)
    
    def enhanced_chat_response(self, user_id: str, character: str, message: str) -> Dict:
        """Generate chat response enhanced with memory context."""
        
        # 1. Get memory context
        context = self.get_conversation_context(user_id, character)
        
        # 2. Get current emotional state
        emotion_state = self.get_current_emotion(user_id, character)
        
        # 3. Prepare enhanced prompt with context
        enhanced_prompt = self._build_contextual_prompt(
            message, context, emotion_state, character
        )
        
        # 4. Send to chat API (assuming your chat API structure)
        try:
            chat_response = requests.post(f"{self.chat_api}/chat", json={
                'message': enhanced_prompt,
                'character': character,
                'user_id': user_id,
                'context': context
            })
            
            if chat_response.status_code == 200:
                response_data = chat_response.json()
                character_response = response_data.get('response', '')
                
                # 5. Store conversation in memory
                self.store_conversation_memory(
                    user_id, character, message, character_response,
                    emotion=emotion_state.get('primary_emotion'),
                    importance=self._calculate_conversation_importance(message, character_response)
                )
                
                # 6. Update emotion if detected in conversation
                detected_emotion = self._detect_emotion_from_text(message)
                if detected_emotion:
                    self.update_emotion(user_id, character, detected_emotion, 
                                      intensity=0.6, trigger=message[:100])
                
                return {
                    'success': True,
                    'response': character_response,
                    'emotion_state': emotion_state,
                    'memory_context': context
                }
            else:
                return {'success': False, 'error': 'Chat API request failed'}
                
        except Exception as e:
            return {'success': False, 'error': f'Chat integration error: {str(e)}'}
    
    # Integration with Voice System (waifu-voice-synthesis)
    
    def emotionally_aware_speech(self, user_id: str, character: str, text: str) -> Dict:
        """Generate speech with emotional awareness from memory."""
        
        # 1. Get current emotional state
        emotion_state = self.get_current_emotion(user_id, character)
        
        # 2. Adjust voice parameters based on emotion
        voice_params = self._emotion_to_voice_params(emotion_state)
        
        # 3. Send to voice synthesis API
        try:
            voice_response = requests.post(f"{self.voice_api}/synthesize", json={
                'text': text,
                'character': character,
                'emotion': emotion_state.get('primary_emotion', 'neutral'),
                'intensity': emotion_state.get('intensity', 0.5),
                **voice_params
            })
            
            if voice_response.status_code == 200:
                return {
                    'success': True,
                    'audio_data': voice_response.content,
                    'emotion_applied': emotion_state,
                    'voice_params': voice_params
                }
            else:
                return {'success': False, 'error': 'Voice API request failed'}
                
        except Exception as e:
            return {'success': False, 'error': f'Voice integration error: {str(e)}'}
    
    # Helper Methods
    
    def _build_contextual_prompt(self, message: str, context: Dict, 
                               emotion_state: Dict, character: str) -> str:
        """Build an enhanced prompt with memory context."""
        
        prompt_parts = [f"As {character}, respond to: {message}"]
        
        # Add recent memories
        recent_memories = context.get('recent_memories', [])
        if recent_memories:
            memory_context = "\\n".join([
                f"- {mem['content']}" for mem in recent_memories[:3]
            ])
            prompt_parts.append(f"\\nRecent context:\\n{memory_context}")
        
        # Add emotional context
        if emotion_state.get('primary_emotion'):
            emotion_context = f"Current emotional state: {emotion_state['primary_emotion']} (intensity: {emotion_state.get('intensity', 0.5)})"
            prompt_parts.append(f"\\n{emotion_context}")
        
        # Add conversation themes
        themes = context.get('conversation_themes', [])
        if themes:
            theme_context = f"Recent topics: {', '.join(themes[:5])}"
            prompt_parts.append(f"\\n{theme_context}")
        
        return "\\n".join(prompt_parts)
    
    def _calculate_conversation_importance(self, user_message: str, 
                                         character_response: str) -> float:
        """Calculate importance of a conversation turn."""
        base_importance = 0.4
        
        # Increase importance for longer messages
        if len(user_message) > 100:
            base_importance += 0.1
        
        # Increase importance for emotional keywords
        emotional_keywords = ['love', 'hate', 'excited', 'sad', 'angry', 'happy']
        emotion_count = sum(1 for word in emotional_keywords 
                          if word in user_message.lower())
        base_importance += emotion_count * 0.05
        
        # Increase importance for personal information
        personal_keywords = ['my', 'i am', 'i like', 'i hate', 'family', 'work']
        personal_count = sum(1 for word in personal_keywords 
                           if word in user_message.lower())
        base_importance += personal_count * 0.03
        
        return min(1.0, base_importance)
    
    def _detect_emotion_from_text(self, text: str) -> Optional[str]:
        """Simple emotion detection from text."""
        emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'awesome', 'love'],
            'sad': ['sad', 'depressed', 'unhappy', 'cry', 'tears'],
            'angry': ['angry', 'mad', 'furious', 'hate', 'annoying'],
            'surprised': ['wow', 'surprised', 'amazing', 'incredible'],
            'curious': ['why', 'how', 'what', 'curious', 'wonder']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return None
    
    def _emotion_to_voice_params(self, emotion_state: Dict) -> Dict:
        """Convert emotion state to voice synthesis parameters."""
        emotion = emotion_state.get('primary_emotion', 'neutral')
        intensity = emotion_state.get('intensity', 0.5)
        
        # Base parameters
        params = {
            'speed': 1.0,
            'pitch': 0.0,
            'volume': 1.0
        }
        
        # Emotion-specific adjustments
        emotion_mappings = {
            'happy': {'speed': 1.1, 'pitch': 0.1, 'volume': 1.05},
            'excited': {'speed': 1.2, 'pitch': 0.2, 'volume': 1.1},
            'sad': {'speed': 0.9, 'pitch': -0.1, 'volume': 0.9},
            'angry': {'speed': 1.1, 'pitch': 0.05, 'volume': 1.1},
            'surprised': {'speed': 1.15, 'pitch': 0.15, 'volume': 1.05},
            'curious': {'speed': 1.05, 'pitch': 0.05, 'volume': 1.0}
        }
        
        if emotion in emotion_mappings:
            emotion_params = emotion_mappings[emotion]
            for param, value in emotion_params.items():
                # Apply intensity scaling
                if param == 'speed':
                    params[param] = 1.0 + (value - 1.0) * intensity
                elif param == 'pitch':
                    params[param] = value * intensity
                elif param == 'volume':
                    params[param] = 1.0 + (value - 1.0) * intensity
        
        return params

# Example Usage
if __name__ == "__main__":
    # Initialize integration
    integration = WaifuMemoryIntegration()
    
    # Example conversation flow
    user_id = "user_123"
    character = "sakura_ai"
    
    print("🧠 Waifu Memory Engine Integration Example")
    print("=" * 50)
    
    # 1. Store a user preference
    print("\\n📝 Storing user preference...")
    pref_result = integration.store_user_preference(
        user_id, character, 
        "User loves cats and enjoys reading manga"
    )
    print(f"Result: {pref_result}")
    
    # 2. Enhanced chat with memory context
    print("\\n💬 Enhanced chat response...")
    user_message = "I'm feeling a bit down today"
    chat_result = integration.enhanced_chat_response(user_id, character, user_message)
    print(f"Enhanced Response: {chat_result.get('response', 'N/A')}")
    
    # 3. Emotionally aware speech synthesis
    print("\\n🎵 Emotionally aware speech...")
    if chat_result.get('success'):
        speech_result = integration.emotionally_aware_speech(
            user_id, character, chat_result['response']
        )
        print(f"Voice synthesis with emotion: {speech_result.get('emotion_applied', {})}")
    
    # 4. Store a milestone
    print("\\n🎯 Storing relationship milestone...")
    milestone_result = integration.store_relationship_milestone(
        user_id, character,
        "User shared personal feelings for the first time"
    )
    print(f"Milestone stored: {milestone_result}")
    
    print("\\n✅ Integration example completed!")
    print("\\nThis demonstrates how the Memory Engine can enhance")
    print("both your chat and voice systems with persistent memory,")
    print("emotional awareness, and contextual understanding.")
