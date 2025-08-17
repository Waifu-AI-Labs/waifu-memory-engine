"""
Example: How to query "What does user like?" and find associated memories
"""
import requests
import json

def analyze_user_preferences(user_id, character, api_base="http://localhost:5003"):
    """
    Comprehensive analysis of user preferences with memory associations.
    """
    
    # Step 1: Get all user preferences
    print("🔍 Step 1: Retrieving user preferences...")
    prefs_response = requests.post(f"{api_base}/memory/preferences", json={
        "user_id": user_id,
        "character": character,
        "min_importance": 0.3
    })
    
    preferences = prefs_response.json()
    
    if not preferences['success']:
        return {"error": "Could not retrieve preferences"}
    
    # Step 2: Analyze preference categories
    print("📊 Step 2: Analyzing preference categories...")
    categorized = preferences['preferences']['categorized']
    
    analysis = {
        "total_preferences": preferences['preferences']['total_count'],
        "categories": {
            "food": len(categorized.get('food', [])),
            "activities": len(categorized.get('activities', [])),
            "personality": len(categorized.get('personality', [])),
            "relationships": len(categorized.get('relationships', [])),
            "other": len(categorized.get('other', []))
        },
        "top_preferences": [],
        "associated_keywords": [],
        "preference_strength": {}
    }
    
    # Step 3: Extract and analyze keywords from all preferences
    print("🔤 Step 3: Extracting keywords for association analysis...")
    all_pref_content = " ".join([
        pref['content'] for pref in preferences['preferences']['all']
    ])
    
    if all_pref_content:
        keywords_response = requests.post(f"{api_base}/analysis/keywords", json={
            "text": all_pref_content,
            "max_keywords": 20
        })
        
        if keywords_response.json()['success']:
            analysis['associated_keywords'] = keywords_response.json()['keywords']
    
    # Step 4: Rank preferences by importance
    print("⭐ Step 4: Ranking preferences by importance...")
    sorted_prefs = sorted(
        preferences['preferences']['all'], 
        key=lambda x: x['importance'], 
        reverse=True
    )
    
    analysis['top_preferences'] = [
        {
            "content": pref['content'],
            "importance": pref['importance'],
            "keywords": pref.get('metadata', {}).get('auto_keywords', [])
        }
        for pref in sorted_prefs[:10]  # Top 10
    ]
    
    # Step 5: Find related memories through keyword associations
    print("🔗 Step 5: Finding associated memories...")
    associated_memories = []
    
    for keyword in analysis['associated_keywords'][:5]:  # Top 5 keywords
        related_response = requests.post(f"{api_base}/memory/retrieve", json={
            "user_id": user_id,
            "character": character,
            "query": keyword,
            "limit": 5,
            "min_importance": 0.4
        })
        
        if related_response.json()['success']:
            memories = related_response.json()['memories']
            for memory in memories:
                if memory['memory_type'] != 'preference':  # Find non-preference associations
                    associated_memories.append({
                        "content": memory['content'],
                        "type": memory['memory_type'],
                        "associated_keyword": keyword,
                        "importance": memory['importance']
                    })
    
    analysis['associated_memories'] = associated_memories
    
    # Step 6: Generate preference summary
    print("📝 Step 6: Generating preference summary...")
    analysis['summary'] = generate_preference_summary(analysis)
    
    return analysis

def generate_preference_summary(analysis):
    """Generate human-readable summary of user preferences."""
    
    summary = []
    
    # Overall stats
    total = analysis['total_preferences']
    summary.append(f"User has {total} stored preferences.")
    
    # Category breakdown
    categories = analysis['categories']
    top_category = max(categories.items(), key=lambda x: x[1])
    if top_category[1] > 0:
        summary.append(f"Most preferences are about {top_category[0]} ({top_category[1]} items).")
    
    # Top preferences
    if analysis['top_preferences']:
        top_pref = analysis['top_preferences'][0]
        summary.append(f"Strongest preference: {top_pref['content']} (importance: {top_pref['importance']:.2f})")
    
    # Keyword themes
    if analysis['associated_keywords']:
        top_keywords = analysis['associated_keywords'][:3]
        summary.append(f"Common themes: {', '.join(top_keywords)}")
    
    # Associations
    if analysis['associated_memories']:
        assoc_count = len(analysis['associated_memories'])
        summary.append(f"Found {assoc_count} related memories from conversations and events.")
    
    return " ".join(summary)

def query_what_user_likes(user_id, character):
    """
    Main function to answer: "What does user like?"
    """
    print(f"🤖 Analyzing what {user_id} likes about {character}...")
    print("=" * 50)
    
    analysis = analyze_user_preferences(user_id, character)
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    # Display results
    print(f"\n📊 PREFERENCE ANALYSIS RESULTS")
    print("-" * 30)
    print(f"Total Preferences: {analysis['total_preferences']}")
    print(f"Categories: {analysis['categories']}")
    print(f"\nTop Keywords: {analysis['associated_keywords'][:10]}")
    
    print(f"\n⭐ TOP PREFERENCES:")
    for i, pref in enumerate(analysis['top_preferences'][:5], 1):
        print(f"{i}. {pref['content']} (importance: {pref['importance']:.2f})")
        if pref['keywords']:
            print(f"   Keywords: {', '.join(pref['keywords'])}")
    
    print(f"\n🔗 ASSOCIATED MEMORIES:")
    for assoc in analysis['associated_memories'][:5]:
        print(f"- {assoc['content']} (via '{assoc['associated_keyword']}')")
    
    print(f"\n📝 SUMMARY:")
    print(analysis['summary'])
    
    return analysis

# Example usage for building chat responses
def build_personalized_response(user_id, character, user_query):
    """
    Example: How to use preference analysis in chat responses
    """
    
    # Get user preferences
    analysis = analyze_user_preferences(user_id, character)
    
    if 'error' in analysis:
        return "I don't have enough information about your preferences yet."
    
    # Extract key information
    top_prefs = [pref['content'] for pref in analysis['top_preferences'][:3]]
    keywords = analysis['associated_keywords'][:5]
    
    # Build context-aware response
    if "like" in user_query.lower() or "prefer" in user_query.lower():
        response_parts = [
            f"Based on our conversations, I know you have {analysis['total_preferences']} preferences stored.",
            f"Your top preferences include: {'; '.join(top_prefs[:2])}.",
            f"I've also noticed you often mention: {', '.join(keywords[:3])}.",
        ]
        
        # Add category-specific insights
        categories = analysis['categories']
        if categories['food'] > 0:
            response_parts.append(f"You seem to have {categories['food']} food-related preferences.")
        if categories['activities'] > 0:
            response_parts.append(f"And {categories['activities']} activity preferences.")
        
        return " ".join(response_parts)
    
    return "Tell me more about what you like, and I'll remember it!"

if __name__ == "__main__":
    # Example usage
    user_id = "alice"
    character = "sakura_ai"
    
    print("🧠 Waifu Memory Engine - Preference Analysis Demo")
    print("=" * 60)
    
    # Simulate some stored preferences first
    print("First, let's simulate storing some preferences...")
    
    sample_preferences = [
        "User loves chocolate ice cream and cats",
        "User enjoys watching anime, especially romantic comedies", 
        "User prefers quiet evenings over loud parties",
        "User likes cooking Japanese food",
        "User enjoys reading manga before bedtime"
    ]
    
    print(f"Sample preferences to analyze: {len(sample_preferences)}")
    
    # Now analyze what the user likes
    analysis = query_what_user_likes(user_id, character)
    
    print("\n" + "="*60)
    print("🎯 CHAT RESPONSE EXAMPLE:")
    print("-" * 30)
    
    sample_query = "What do you think I like?"
    response = build_personalized_response(user_id, character, sample_query)
    print(f"User: {sample_query}")
    print(f"AI: {response}")
