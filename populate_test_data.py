"""
Quick script to populate test data for the memory engine
"""
import requests
import json

def populate_test_data():
    api_base = "http://localhost:5003"
    user_id = "user123"
    character = "sakura_ai"
    
    print("🧠 Populating Memory Engine with Test Data...")
    
    # Test memories to add
    test_memories = [
        {
            "content": "User loves chocolate ice cream and cats",
            "memory_type": "preference",
            "importance": 0.8,
            "emotion": "happy"
        },
        {
            "content": "User enjoys watching romantic anime",
            "memory_type": "preference", 
            "importance": 0.7,
            "emotion": "excited"
        },
        {
            "content": "User said: Hello, how are you today?",
            "memory_type": "conversation",
            "importance": 0.4
        },
        {
            "content": "I responded: I'm doing great! Thanks for asking!",
            "memory_type": "conversation",
            "importance": 0.4,
            "emotion": "happy"
        },
        {
            "content": "User prefers quiet evenings over loud parties",
            "memory_type": "preference",
            "importance": 0.6
        },
        {
            "content": "User likes cooking Japanese food",
            "memory_type": "preference",
            "importance": 0.7,
            "emotion": "content"
        },
        {
            "content": "We had a great conversation about anime",
            "memory_type": "event",
            "importance": 0.8,
            "emotion": "happy"
        }
    ]
    
    # Store each memory
    for i, memory in enumerate(test_memories, 1):
        try:
            response = requests.post(f"{api_base}/memory/store", json={
                "user_id": user_id,
                "character": character,
                **memory
            })
            
            result = response.json()
            if result.get('success'):
                print(f"✅ {i}. Stored: {memory['content'][:50]}...")
            else:
                print(f"❌ {i}. Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ {i}. Error: {str(e)}")
    
    print(f"\n🎯 Test data population complete!")
    
    # Test retrieval
    print("\n📊 Testing retrieval...")
    try:
        response = requests.post(f"{api_base}/memory/preferences", json={
            "user_id": user_id,
            "character": character
        })
        
        result = response.json()
        if result.get('success'):
            count = result['preferences']['total_count']
            print(f"✅ Found {count} preferences")
            
            for pref in result['preferences']['all'][:3]:
                print(f"  - {pref['content']} (importance: {pref['importance']})")
        else:
            print(f"❌ Retrieval failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Retrieval error: {str(e)}")

if __name__ == "__main__":
    populate_test_data()
