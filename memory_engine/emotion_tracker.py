import json
import uuid
from datetime import datetime, timedelta
from .database import get_db_connection

class EmotionTracker:
    """Tracks and manages emotional states for waifu characters."""
    
    def __init__(self):
        self.emotion_categories = {
            'positive': ['happy', 'excited', 'cheerful', 'content', 'loving', 'proud', 'grateful'],
            'negative': ['sad', 'angry', 'frustrated', 'disappointed', 'worried', 'lonely'],
            'neutral': ['calm', 'neutral', 'curious', 'thoughtful', 'focused'],
            'special': ['embarrassed', 'surprised', 'confused', 'mischievous', 'sleepy']
        }
        
        self.emotion_intensities = {
            'subtle': (0.1, 0.3),
            'moderate': (0.4, 0.6), 
            'strong': (0.7, 0.9),
            'intense': (0.9, 1.0)
        }
    
    def set_emotion(self, user_id, character, emotion, intensity, context=None, duration=3600):
        """Set current emotional state for a character."""
        if intensity < 0.0 or intensity > 1.0:
            return {
                'success': False,
                'error': 'Intensity must be between 0.0 and 1.0'
            }
        
        emotion_id = str(uuid.uuid4())
        conn = get_db_connection()
        
        try:
            # Store the emotional state
            conn.execute('''
                INSERT INTO emotional_states 
                (id, user_id, character, emotion, intensity, context, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (emotion_id, user_id, character, emotion, intensity, context, duration))
            
            conn.commit()
            
            # Update personality traits based on emotional patterns
            self._update_personality_from_emotion(conn, user_id, character, emotion, intensity)
            
            return {
                'success': True,
                'emotion_id': emotion_id,
                'message': f'Emotion "{emotion}" set with intensity {intensity}',
                'emotion': emotion,
                'intensity': intensity,
                'context': context
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_current_emotion(self, user_id, character):
        """Get the current active emotional state."""
        conn = get_db_connection()
        try:
            # Get the most recent emotion within its duration
            row = conn.execute('''
                SELECT emotion, intensity, context, timestamp, duration
                FROM emotional_states 
                WHERE user_id = ? AND character = ?
                AND datetime(timestamp, '+' || duration || ' seconds') > datetime('now')
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (user_id, character)).fetchone()
            
            if row:
                return {
                    'success': True,
                    'emotion': row['emotion'],
                    'intensity': row['intensity'],
                    'context': row['context'],
                    'timestamp': row['timestamp'],
                    'remaining_duration': self._calculate_remaining_duration(row['timestamp'], row['duration'])
                }
            else:
                return {
                    'success': True,
                    'emotion': 'neutral',
                    'intensity': 0.5,
                    'context': 'default state',
                    'timestamp': datetime.now().isoformat(),
                    'remaining_duration': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_emotion_history(self, user_id, character, hours=24, limit=50):
        """Get recent emotional history."""
        conn = get_db_connection()
        try:
            # Get emotions from the last N hours
            rows = conn.execute('''
                SELECT emotion, intensity, context, timestamp, duration
                FROM emotional_states 
                WHERE user_id = ? AND character = ?
                AND timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(hours), (user_id, character, limit)).fetchall()
            
            emotions = []
            for row in rows:
                emotions.append({
                    'emotion': row['emotion'],
                    'intensity': row['intensity'],
                    'context': row['context'],
                    'timestamp': row['timestamp'],
                    'duration': row['duration']
                })
            
            # Calculate emotion patterns
            patterns = self._analyze_emotion_patterns(emotions)
            
            return {
                'success': True,
                'emotions': emotions,
                'patterns': patterns,
                'period_hours': hours
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def transition_emotion(self, user_id, character, new_emotion, new_intensity, 
                          transition_reason=None, duration=3600):
        """Smoothly transition from current emotion to new emotion."""
        current_result = self.get_current_emotion(user_id, character)
        
        if current_result['success']:
            current_emotion = current_result['emotion']
            current_intensity = current_result['intensity']
            
            # Calculate transition appropriateness
            transition_score = self._calculate_transition_score(
                current_emotion, current_intensity, 
                new_emotion, new_intensity
            )
            
            # Store transition context
            context = f"Transitioned from {current_emotion}({current_intensity:.1f}) to {new_emotion}({new_intensity:.1f})"
            if transition_reason:
                context += f" - {transition_reason}"
            
            # Set new emotion
            result = self.set_emotion(user_id, character, new_emotion, new_intensity, context, duration)
            
            if result['success']:
                result['transition_score'] = transition_score
                result['previous_emotion'] = current_emotion
                result['previous_intensity'] = current_intensity
            
            return result
        else:
            # Fallback to regular set_emotion if can't get current state
            return self.set_emotion(user_id, character, new_emotion, new_intensity, 
                                  transition_reason, duration)
    
    def get_emotional_compatibility(self, user_id, character, target_emotion):
        """Check how well a target emotion fits with current emotional state."""
        current = self.get_current_emotion(user_id, character)
        
        if not current['success']:
            return {
                'success': False,
                'error': 'Could not get current emotional state'
            }
        
        compatibility_score = self._calculate_emotion_compatibility(
            current['emotion'], target_emotion
        )
        
        category_current = self._get_emotion_category(current['emotion'])
        category_target = self._get_emotion_category(target_emotion)
        
        return {
            'success': True,
            'current_emotion': current['emotion'],
            'target_emotion': target_emotion,
            'compatibility_score': compatibility_score,
            'current_category': category_current,
            'target_category': category_target,
            'recommendation': self._get_compatibility_recommendation(compatibility_score)
        }
    
    def _calculate_remaining_duration(self, timestamp_str, duration):
        """Calculate remaining duration for an emotion in seconds."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            expiry = timestamp + timedelta(seconds=duration)
            remaining = (expiry - datetime.now()).total_seconds()
            return max(0, int(remaining))
        except:
            return 0
    
    def _update_personality_from_emotion(self, conn, user_id, character, emotion, intensity):
        """Update personality traits based on emotional patterns."""
        from .personality import PersonalityManager
        
        # Define emotion-to-trait mappings
        emotion_trait_effects = {
            'happy': {'cheerfulness': 0.01, 'confidence': 0.005},
            'sad': {'cheerfulness': -0.005, 'shyness': 0.005},
            'excited': {'playfulness': 0.01, 'spontaneity': 0.01},
            'angry': {'confidence': 0.005, 'empathy': -0.005},
            'caring': {'caring': 0.01, 'empathy': 0.01},
            'embarrassed': {'shyness': 0.01, 'confidence': -0.005},
            'proud': {'confidence': 0.01, 'cheerfulness': 0.005}
        }
        
        if emotion in emotion_trait_effects:
            personality_mgr = PersonalityManager()
            
            for trait, adjustment in emotion_trait_effects[emotion].items():
                # Scale adjustment by intensity
                scaled_adjustment = adjustment * intensity
                
                personality_mgr.adjust_trait(
                    user_id, character, trait, scaled_adjustment,
                    f"Emotional influence from {emotion} (intensity: {intensity:.1f})"
                )
    
    def _analyze_emotion_patterns(self, emotions):
        """Analyze patterns in emotional history."""
        if not emotions:
            return {}
        
        # Count emotions by category
        category_counts = {'positive': 0, 'negative': 0, 'neutral': 0, 'special': 0}
        total_intensity = 0
        
        for emotion_data in emotions:
            category = self._get_emotion_category(emotion_data['emotion'])
            category_counts[category] += 1
            total_intensity += emotion_data['intensity']
        
        total_count = len(emotions)
        avg_intensity = total_intensity / total_count if total_count > 0 else 0
        
        # Determine dominant mood
        dominant_category = max(category_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_emotions': total_count,
            'average_intensity': avg_intensity,
            'category_distribution': category_counts,
            'dominant_mood_category': dominant_category,
            'mood_stability': self._calculate_mood_stability(emotions)
        }
    
    def _calculate_transition_score(self, from_emotion, from_intensity, to_emotion, to_intensity):
        """Calculate how natural an emotional transition is."""
        # Base compatibility between emotions
        compatibility = self._calculate_emotion_compatibility(from_emotion, to_emotion)
        
        # Intensity change factor
        intensity_change = abs(to_intensity - from_intensity)
        intensity_factor = 1.0 - (intensity_change * 0.5)  # Penalize large intensity jumps
        
        # Overall transition score
        return compatibility * 0.7 + intensity_factor * 0.3
    
    def _calculate_emotion_compatibility(self, emotion1, emotion2):
        """Calculate compatibility score between two emotions."""
        if emotion1 == emotion2:
            return 1.0
        
        category1 = self._get_emotion_category(emotion1)
        category2 = self._get_emotion_category(emotion2)
        
        # Same category emotions are more compatible
        if category1 == category2:
            return 0.8
        
        # Define compatibility matrix
        compatibility_matrix = {
            ('positive', 'neutral'): 0.7,
            ('neutral', 'positive'): 0.7,
            ('negative', 'neutral'): 0.6,
            ('neutral', 'negative'): 0.6,
            ('positive', 'special'): 0.5,
            ('special', 'positive'): 0.5,
            ('negative', 'special'): 0.4,
            ('special', 'negative'): 0.4,
            ('positive', 'negative'): 0.2,
            ('negative', 'positive'): 0.2,
        }
        
        return compatibility_matrix.get((category1, category2), 0.3)
    
    def _get_emotion_category(self, emotion):
        """Get the category of an emotion."""
        for category, emotions in self.emotion_categories.items():
            if emotion in emotions:
                return category
        return 'neutral'
    
    def _calculate_mood_stability(self, emotions):
        """Calculate mood stability based on emotion changes."""
        if len(emotions) < 2:
            return 1.0
        
        stability_score = 1.0
        for i in range(1, len(emotions)):
            prev = emotions[i-1]
            curr = emotions[i]
            
            # Penalize category changes
            if self._get_emotion_category(prev['emotion']) != self._get_emotion_category(curr['emotion']):
                stability_score -= 0.1
            
            # Penalize large intensity changes
            intensity_change = abs(curr['intensity'] - prev['intensity'])
            stability_score -= intensity_change * 0.05
        
        return max(0.0, stability_score)
    
    def _get_compatibility_recommendation(self, score):
        """Get human-readable recommendation based on compatibility score."""
        if score > 0.8:
            return "Excellent transition - very natural"
        elif score > 0.6:
            return "Good transition - feels natural"
        elif score > 0.4:
            return "Moderate transition - acceptable with context"
        elif score > 0.2:
            return "Challenging transition - needs strong context"
        else:
            return "Difficult transition - consider gradual change"
