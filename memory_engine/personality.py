import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .database import get_db_connection

class PersonalityManager:
    """
    Advanced personality management system for waifu characters.
    Handles trait evolution, mood states, and personality-driven interactions.
    """
    
    def __init__(self):
        self.default_traits = {
            'cheerfulness': 0.7,
            'shyness': 0.3,
            'playfulness': 0.6,
            'caring': 0.8,
            'intelligence': 0.7,
            'curiosity': 0.6,
            'loyalty': 0.9,
            'empathy': 0.8,
            'confidence': 0.5,
            'spontaneity': 0.4,
            'romanticism': 0.6,
            'protectiveness': 0.7,
            'mischievousness': 0.3,
            'patience': 0.6
        }
        
        self.personality_profiles = {
            'tsundere': {
                'shyness': 0.8, 'confidence': 0.3, 'caring': 0.9, 'mischievousness': 0.6,
                'loyalty': 0.9, 'empathy': 0.7, 'romanticism': 0.8, 'cheerfulness': 0.4
            },
            'kuudere': {
                'shyness': 0.4, 'confidence': 0.8, 'intelligence': 0.9, 'caring': 0.8,
                'empathy': 0.6, 'cheerfulness': 0.3, 'loyalty': 0.9, 'patience': 0.9
            },
            'dandere': {
                'shyness': 0.9, 'caring': 0.9, 'empathy': 0.9, 'intelligence': 0.8,
                'confidence': 0.2, 'cheerfulness': 0.6, 'loyalty': 0.9, 'patience': 0.8
            },
            'yandere': {
                'loyalty': 1.0, 'protectiveness': 1.0, 'romanticism': 1.0, 'caring': 0.9,
                'confidence': 0.7, 'shyness': 0.3, 'empathy': 0.5, 'mischievousness': 0.8
            },
            'genki': {
                'cheerfulness': 1.0, 'playfulness': 0.9, 'spontaneity': 0.9, 'confidence': 0.8,
                'curiosity': 0.9, 'empathy': 0.8, 'caring': 0.8, 'shyness': 0.1
            },
            'ojousama': {
                'confidence': 0.9, 'intelligence': 0.8, 'cheerfulness': 0.7, 'caring': 0.6,
                'romanticism': 0.7, 'patience': 0.4, 'shyness': 0.2, 'protectiveness': 0.5
            }
        }
        
        self.mood_states = {
            'happy': {'cheerfulness': 0.3, 'playfulness': 0.2, 'confidence': 0.1},
            'sad': {'cheerfulness': -0.3, 'empathy': 0.2, 'shyness': 0.1},
            'excited': {'cheerfulness': 0.2, 'spontaneity': 0.3, 'playfulness': 0.2},
            'angry': {'patience': -0.3, 'mischievousness': 0.2, 'confidence': 0.2},
            'shy': {'shyness': 0.3, 'confidence': -0.2, 'caring': 0.1},
            'loving': {'romanticism': 0.3, 'caring': 0.2, 'empathy': 0.2},
            'playful': {'playfulness': 0.3, 'mischievousness': 0.2, 'spontaneity': 0.1},
            'protective': {'protectiveness': 0.3, 'loyalty': 0.2, 'caring': 0.1},
            'curious': {'curiosity': 0.3, 'intelligence': 0.1, 'confidence': 0.1},
            'mischievous': {'mischievousness': 0.3, 'playfulness': 0.2, 'confidence': 0.1}
        }
    
    def initialize_personality(self, user_id, character):
        """Initialize default personality traits for a character."""
        conn = get_db_connection()
        try:
            # Check if personality already exists
            existing = conn.execute('''
                SELECT COUNT(*) as count FROM personality_traits 
                WHERE user_id = ? AND character = ?
            ''', (user_id, character)).fetchone()
            
            if existing['count'] > 0:
                return {
                    'success': True,
                    'message': 'Personality already initialized'
                }
            
            # Insert default traits
            for trait_name, trait_value in self.default_traits.items():
                trait_id = str(uuid.uuid4())
                conn.execute('''
                    INSERT INTO personality_traits 
                    (id, user_id, character, trait_name, trait_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (trait_id, user_id, character, trait_name, trait_value))
            
            conn.commit()
            
            return {
                'success': True,
                'message': 'Personality initialized with default traits',
                'traits': self.default_traits
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_personality(self, user_id, character):
        """Get current personality traits for a character."""
        conn = get_db_connection()
        try:
            rows = conn.execute('''
                SELECT trait_name, trait_value, last_updated
                FROM personality_traits 
                WHERE user_id = ? AND character = ?
                ORDER BY trait_name
            ''', (user_id, character)).fetchall()
            
            if not rows:
                # Initialize with defaults if no personality exists
                init_result = self.initialize_personality(user_id, character)
                if init_result['success']:
                    return self.get_personality(user_id, character)
                else:
                    return init_result
            
            traits = {}
            for row in rows:
                traits[row['trait_name']] = {
                    'value': row['trait_value'],
                    'last_updated': row['last_updated']
                }
            
            return {
                'success': True,
                'traits': traits,
                'character': character
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def update_trait(self, user_id, character, trait_name, trait_value):
        """Update a specific personality trait."""
        if trait_value < 0.0 or trait_value > 1.0:
            return {
                'success': False,
                'error': 'Trait value must be between 0.0 and 1.0'
            }
        
        conn = get_db_connection()
        try:
            # Check if trait exists
            existing = conn.execute('''
                SELECT id FROM personality_traits 
                WHERE user_id = ? AND character = ? AND trait_name = ?
            ''', (user_id, character, trait_name)).fetchone()
            
            if existing:
                # Update existing trait
                conn.execute('''
                    UPDATE personality_traits 
                    SET trait_value = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND character = ? AND trait_name = ?
                ''', (trait_value, user_id, character, trait_name))
            else:
                # Insert new trait
                trait_id = str(uuid.uuid4())
                conn.execute('''
                    INSERT INTO personality_traits 
                    (id, user_id, character, trait_name, trait_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (trait_id, user_id, character, trait_name, trait_value))
            
            conn.commit()
            
            return {
                'success': True,
                'message': f'Trait "{trait_name}" updated to {trait_value}',
                'trait_name': trait_name,
                'trait_value': trait_value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def adjust_trait(self, user_id, character, trait_name, adjustment, reason=None):
        """Gradually adjust a trait based on interactions."""
        conn = get_db_connection()
        try:
            # Get current trait value
            current = conn.execute('''
                SELECT trait_value FROM personality_traits 
                WHERE user_id = ? AND character = ? AND trait_name = ?
            ''', (user_id, character, trait_name)).fetchone()
            
            if not current:
                # Initialize if trait doesn't exist
                current_value = self.default_traits.get(trait_name, 0.5)
            else:
                current_value = current['trait_value']
            
            # Apply adjustment (clamped between 0 and 1)
            new_value = max(0.0, min(1.0, current_value + adjustment))
            
            # Update the trait
            result = self.update_trait(user_id, character, trait_name, new_value)
            
            if result['success'] and reason:
                # Store the adjustment reason as metadata
                from .memory_manager import MemoryManager
                memory_mgr = MemoryManager()
                memory_mgr.store_memory(
                    user_id=user_id,
                    character=character,
                    content=f"Personality trait '{trait_name}' adjusted from {current_value:.2f} to {new_value:.2f}. Reason: {reason}",
                    memory_type="personality_change",
                    importance=0.6,
                    metadata={
                        'trait_name': trait_name,
                        'old_value': current_value,
                        'new_value': new_value,
                        'adjustment': adjustment,
                        'reason': reason
                    }
                )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_personality_summary(self, user_id, character):
        """Get a human-readable personality summary."""
        result = self.get_personality(user_id, character)
        
        if not result['success']:
            return result
        
        traits = result['traits']
        
        # Generate personality description based on dominant traits
        dominant_traits = []
        for trait_name, trait_data in traits.items():
            if trait_data['value'] > 0.7:
                dominant_traits.append(trait_name)
        
        # Personality archetypes based on trait combinations
        archetype = self._determine_archetype(traits)
        
        return {
            'success': True,
            'character': character,
            'archetype': archetype,
            'dominant_traits': dominant_traits,
            'traits': traits,
            'summary': self._generate_personality_text(traits, archetype)
        }
    
    def _determine_archetype(self, traits):
        """Determine personality archetype based on trait combinations."""
        values = {k: v['value'] for k, v in traits.items()}
        
        if values.get('shyness', 0) > 0.7 and values.get('caring', 0) > 0.7:
            return "shy_caring"
        elif values.get('cheerfulness', 0) > 0.7 and values.get('playfulness', 0) > 0.7:
            return "cheerful_playful"
        elif values.get('intelligence', 0) > 0.7 and values.get('curiosity', 0) > 0.7:
            return "intellectual_curious"
        elif values.get('confidence', 0) > 0.7 and values.get('loyalty', 0) > 0.7:
            return "confident_loyal"
        elif values.get('empathy', 0) > 0.7 and values.get('caring', 0) > 0.7:
            return "empathetic_nurturing"
        else:
            return "balanced"
    
    def _generate_personality_text(self, traits, archetype):
        """Generate a human-readable personality description."""
        archetype_descriptions = {
            "shy_caring": "A gentle and caring soul who tends to be reserved but deeply empathetic towards others.",
            "cheerful_playful": "An energetic and joyful personality who brings light and fun to every interaction.",
            "intellectual_curious": "A thoughtful and inquisitive mind who loves learning and exploring new ideas.",
            "confident_loyal": "A strong and dependable character who stands by their beliefs and those they care about.",
            "empathetic_nurturing": "A warm and understanding personality who naturally cares for others' wellbeing.",
            "balanced": "A well-rounded personality with a good balance of various traits."
        }
        
        base_description = archetype_descriptions.get(archetype, "A unique personality.")
        
        # Add specific trait highlights
        trait_highlights = []
        values = {k: v['value'] for k, v in traits.items()}
        
        if values.get('cheerfulness', 0) > 0.8:
            trait_highlights.append("exceptionally cheerful")
        if values.get('shyness', 0) > 0.8:
            trait_highlights.append("quite shy")
        if values.get('intelligence', 0) > 0.8:
            trait_highlights.append("highly intelligent")
        if values.get('playfulness', 0) > 0.8:
            trait_highlights.append("very playful")
        if values.get('loyalty', 0) > 0.9:
            trait_highlights.append("extremely loyal")
        
        if trait_highlights:
            base_description += f" Particularly {', '.join(trait_highlights)}."
        
        return base_description
