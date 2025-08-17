import json
import uuid
from datetime import datetime
from .database import get_db_connection
from .utils import calculate_relevance_score, extract_keywords

class MemoryManager:
    """Core memory management system for waifu characters."""
    
    def __init__(self):
        self.conn = None
    
    def store_memory(self, user_id, character, content, memory_type, emotion=None, 
                    importance=0.5, metadata=None):
        """Store a new memory entry."""
        memory_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO memories 
                (id, user_id, character, content, memory_type, emotion, importance, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (memory_id, user_id, character, content, memory_type, emotion, 
                 importance, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            
            # Update relationship interaction count
            self._update_interaction_count(conn, user_id, character)
            
            return {
                'success': True,
                'memory_id': memory_id,
                'message': 'Memory stored successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def retrieve_memories(self, user_id, character, query=None, memory_type=None, 
                         limit=10, min_importance=0.0):
        """Retrieve relevant memories based on query and filters."""
        conn = get_db_connection()
        try:
            # Base query
            sql = '''
                SELECT id, user_id, character, content, memory_type, emotion, 
                       importance, timestamp, last_accessed, access_count, metadata
                FROM memories 
                WHERE user_id = ? AND character = ? AND importance >= ?
            '''
            params = [user_id, character, min_importance]
            
            # Add memory type filter
            if memory_type:
                sql += ' AND memory_type = ?'
                params.append(memory_type)
            
            # Add content search if query provided
            if query:
                sql += ' AND content LIKE ?'
                params.append(f'%{query}%')
            
            # Order by relevance (importance * recency * access count)
            sql += '''
                ORDER BY 
                    importance * 0.4 + 
                    (julianday('now') - julianday(timestamp)) * -0.001 + 
                    access_count * 0.01 
                DESC 
                LIMIT ?
            '''
            params.append(limit)
            
            rows = conn.execute(sql, params).fetchall()
            
            memories = []
            for row in rows:
                memory = {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'character': row['character'],
                    'content': row['content'],
                    'memory_type': row['memory_type'],
                    'emotion': row['emotion'],
                    'importance': row['importance'],
                    'timestamp': row['timestamp'],
                    'last_accessed': row['last_accessed'],
                    'access_count': row['access_count'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                memories.append(memory)
                
                # Update access count and last accessed time
                self._update_memory_access(conn, row['id'])
            
            conn.commit()
            
            # Calculate relevance scores if query provided
            if query and memories:
                memories = self._score_memories_by_relevance(memories, query)
            
            return {
                'success': True,
                'memories': memories,
                'total_count': len(memories)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'memories': []
            }
        finally:
            conn.close()
    
    def get_memory_summary(self, user_id, character, days=30):
        """Get a summary of recent memory activity."""
        conn = get_db_connection()
        try:
            # Get memory counts by type for the last N days
            memory_stats = conn.execute('''
                SELECT 
                    memory_type,
                    COUNT(*) as count,
                    AVG(importance) as avg_importance
                FROM memories 
                WHERE user_id = ? AND character = ? 
                AND timestamp >= datetime('now', '-{} days')
                GROUP BY memory_type
                ORDER BY count DESC
            '''.format(days), (user_id, character)).fetchall()
            
            # Get most important recent memories
            important_memories = conn.execute('''
                SELECT content, importance, timestamp, memory_type
                FROM memories 
                WHERE user_id = ? AND character = ? 
                AND timestamp >= datetime('now', '-{} days')
                AND importance > 0.7
                ORDER BY importance DESC, timestamp DESC
                LIMIT 5
            '''.format(days), (user_id, character)).fetchall()
            
            return {
                'success': True,
                'memory_stats': [dict(row) for row in memory_stats],
                'important_memories': [dict(row) for row in important_memories],
                'period_days': days
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def update_memory_importance(self, memory_id, new_importance):
        """Update the importance score of a specific memory."""
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE memories 
                SET importance = ? 
                WHERE id = ?
            ''', (new_importance, memory_id))
            
            conn.commit()
            
            return {
                'success': True,
                'message': 'Memory importance updated'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def delete_memory(self, memory_id):
        """Delete a specific memory."""
        conn = get_db_connection()
        try:
            cursor = conn.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {
                    'success': True,
                    'message': 'Memory deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Memory not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def _update_memory_access(self, conn, memory_id):
        """Update access count and last accessed time for a memory."""
        conn.execute('''
            UPDATE memories 
            SET access_count = access_count + 1,
                last_accessed = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (memory_id,))
    
    def _update_interaction_count(self, conn, user_id, character):
        """Update interaction count in relationships table."""
        conn.execute('''
            INSERT OR REPLACE INTO relationships 
            (id, user_id, character, interaction_count, last_interaction)
            VALUES (
                COALESCE(
                    (SELECT id FROM relationships WHERE user_id = ? AND character = ?),
                    ?
                ),
                ?, ?, 
                COALESCE(
                    (SELECT interaction_count FROM relationships WHERE user_id = ? AND character = ?),
                    0
                ) + 1,
                CURRENT_TIMESTAMP
            )
        ''', (user_id, character, str(uuid.uuid4()), user_id, character, user_id, character))
    
    def _score_memories_by_relevance(self, memories, query):
        """Score memories by relevance to query and re-sort."""
        scored_memories = []
        
        for memory in memories:
            relevance = calculate_relevance_score(memory['content'], query)
            memory['relevance_score'] = relevance
            scored_memories.append(memory)
        
        # Sort by combined score (importance + relevance)
        scored_memories.sort(
            key=lambda x: x['importance'] * 0.6 + x['relevance_score'] * 0.4,
            reverse=True
        )
        
        return scored_memories
