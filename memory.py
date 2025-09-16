# memory.py - Zani's Memory System
import json
import os
import datetime
from typing import Dict, List, Any

class ZaniMemory:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()
    
    def load_memory(self) -> Dict:
        """Load memory from JSON file"""
        default_memory = {
            "user_preferences": {
                "name": None,
                "preferred_title": "Sir",
                "mood_preference": "formal",
                "timezone": None,
                "work_schedule": {},
                "interests": []
            },
            "conversation_history": [],
            "reminders": {
                "completed": [],
                "recurring": []
            },
            "learning": {
                "frequent_requests": {},
                "error_patterns": [],
                "successful_interactions": []
            },
            "personal_facts": {},
            "work_patterns": {
                "productive_hours": [],
                "break_preferences": {},
                "project_contexts": []
            },
            "stats": {
                "total_conversations": 0,
                "favorite_features": {},
                "session_count": 0,
                "first_interaction": None,
                "last_interaction": None
            }
        }
        
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    loaded_memory = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self.merge_dicts(default_memory, loaded_memory)
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")
                return default_memory
        
        return default_memory
    
    def save_memory(self):
        """Save memory to JSON file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Error saving memory: {e}")
    
    def merge_dicts(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge dictionaries"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                loaded[key] = self.merge_dicts(value, loaded[key])
        return loaded
    
    def remember_conversation(self, user_input: str, zani_response: str):
        """Store conversation in memory"""
        conversation = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_input,
            "zani": zani_response
        }
        
        # Keep only last 50 conversations to avoid huge files
        self.memory["conversation_history"].append(conversation)
        if len(self.memory["conversation_history"]) > 50:
            self.memory["conversation_history"] = self.memory["conversation_history"][-50:]
        
        # Update stats
        self.memory["stats"]["total_conversations"] += 1
        self.memory["stats"]["last_interaction"] = datetime.datetime.now().isoformat()
        
        if not self.memory["stats"]["first_interaction"]:
            self.memory["stats"]["first_interaction"] = datetime.datetime.now().isoformat()
        
        self.save_memory()
    
    def learn_preference(self, category: str, preference: str, value: Any):
        """Learn user preferences"""
        if category not in self.memory["user_preferences"]:
            self.memory["user_preferences"][category] = {}
        
        self.memory["user_preferences"][category] = value
        self.save_memory()
        return f"I'll remember that you prefer {preference}, {self.get_user_title()}!"
    
    def remember_fact(self, key: str, value: str):
        """Remember personal facts about the user"""
        self.memory["personal_facts"][key] = {
            "value": value,
            "learned_date": datetime.datetime.now().isoformat(),
            "confidence": 1.0
        }
        self.save_memory()
        return f"Got it! I'll remember that {key}: {value}"
    
    def get_user_title(self) -> str:
        """Get preferred user title"""
        return self.memory["user_preferences"].get("preferred_title", "Sir")
    
    def get_mood_preference(self) -> str:
        """Get preferred mood"""
        return self.memory["user_preferences"].get("mood_preference", "formal")
    
    def track_feature_usage(self, feature: str):
        """Track which features are used most"""
        if feature not in self.memory["stats"]["favorite_features"]:
            self.memory["stats"]["favorite_features"][feature] = 0
        
        self.memory["stats"]["favorite_features"][feature] += 1
        self.save_memory()
    
    def get_context_greeting(self) -> str:
        """Get contextual greeting based on memory"""
        total_convs = self.memory["stats"]["total_conversations"]
        user_title = self.get_user_title()
        
        if total_convs == 0:
            return f"Hello {user_title}! I'm Zani, and I'm excited to get to know you better!"
        elif total_convs < 10:
            return f"Good to see you again, {user_title}! I'm still learning about your preferences."
        elif total_convs < 50:
            return f"Welcome back, {user_title}! I'm getting better at understanding what you need."
        else:
            return f"Hello again, {user_title}! Ready for another productive session together?"
    
    def get_memory_summary(self) -> str:
        """Get a summary of what Zani remembers"""
        stats = self.memory["stats"]
        prefs = self.memory["user_preferences"]
        facts_count = len(self.memory["personal_facts"])
        
        summary = f"""
🧠 Memory Summary:
   • Total conversations: {stats['total_conversations']}
   • Your preferred title: {self.get_user_title()}
   • Preferred mood: {self.get_mood_preference()}
   • Personal facts remembered: {facts_count}
   • Most used features: {', '.join(list(stats.get('favorite_features', {}).keys())[:3])}
        """
        
        if stats.get('first_interaction'):
            first_date = datetime.datetime.fromisoformat(stats['first_interaction']).strftime('%B %d, %Y')
            summary += f"\n   • First met: {first_date}"
        
        return summary.strip()
    
    def suggest_based_on_history(self) -> str:
        """Suggest actions based on conversation history"""
        features = self.memory["stats"]["favorite_features"]
        if not features:
            return "Try asking me to set a reminder, tell a joke, or help with calculations!"
        
        top_feature = max(features, key=features.get)
        suggestions = {
            "reminders": "Would you like me to set another reminder?",
            "jokes": "Ready for another joke to brighten your day?",
            "calculations": "Need help with any math today?",
            "time": "Want to check the time or set a schedule?",
        }
        
        return suggestions.get(top_feature, "How can I help you today?")
    
    def learn_from_conversation(self, user_input: str):
        """Automatically learn from conversation patterns"""
        user_lower = user_input.lower()
        
        # Learn name if mentioned
        if "my name is" in user_lower or "i'm " in user_lower or "call me" in user_lower:
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in ["name", "i'm", "call"] and i + 1 < len(words):
                    potential_name = words[i + 1].strip(".,!?")
                    if potential_name.isalpha() and len(potential_name) > 1:
                        self.memory["user_preferences"]["name"] = potential_name
                        self.save_memory()
                        break
        
        # Learn interests
        if any(phrase in user_lower for phrase in ["i like", "i love", "i enjoy", "i'm interested in"]):
            interests = self.memory["user_preferences"]["interests"]
            # Simple keyword extraction (can be improved)
            potential_interests = ["programming", "coding", "music", "games", "sports", "reading", "movies"]
            for interest in potential_interests:
                if interest in user_lower and interest not in interests:
                    interests.append(interest)
                    self.save_memory()
                    break

# Memory instance
memory = ZaniMemory()

# Conversation wrapper function
def remember_conversation(user_input: str, zani_response: str):
    """Wrapper to remember conversations"""
    memory.remember_conversation(user_input, zani_response)
    memory.learn_from_conversation(user_input)

# Memory-enhanced response functions
def get_personalized_greeting() -> str:
    """Get greeting with memory context"""
    return memory.get_context_greeting()

def get_memory_stats() -> str:
    """Get memory statistics"""
    return memory.get_memory_summary()
# Add this function to your memory.py file at the end

def update_memory(entry: Dict[str, Any]):
    """
    General purpose memory update function to handle different entry types
    Compatible with agent.py's update_memory calls
    """
    try:
        entry_type = entry.get("type", "unknown")
        
        if entry_type == "success":
            # Successful AI interaction
            user_query = entry.get("query", "")
            response = entry.get("response", "")
            remember_conversation(user_query, response)
            
            # Track feature usage
            if any(cmd in user_query.lower() for cmd in ["remind", "joke", "time", "date", "calc"]):
                feature = "reminders" if "remind" in user_query.lower() else \
                         "jokes" if "joke" in user_query.lower() else \
                         "time" if "time" in user_query.lower() else \
                         "calculations" if "calc" in user_query.lower() else "other"
                memory.track_feature_usage(feature)
                
        elif entry_type == "rule_based":
            # Rule-based response
            user_query = entry.get("query", "")
            response = entry.get("response", "")
            remember_conversation(user_query, response)
            
        elif entry_type == "error":
            # Error logging
            user_query = entry.get("query", "Unknown query")
            error_msg = entry.get("error", "Unknown error")
            timestamp = entry.get("timestamp", datetime.datetime.now().isoformat())
            
            # Store error in learning section
            error_entry = {
                "query": user_query,
                "error": error_msg,
                "timestamp": timestamp
            }
            
            memory.memory["learning"]["error_patterns"].append(error_entry)
            
            # Keep only last 20 errors to avoid bloat
            if len(memory.memory["learning"]["error_patterns"]) > 20:
                memory.memory["learning"]["error_patterns"] = memory.memory["learning"]["error_patterns"][-20:]
            
            memory.save_memory()
            print(f"[📝] Error logged to memory: {error_msg}")
            
        else:
            print(f"[⚠️] Unknown memory entry type: {entry_type}")
            
    except Exception as e:
        print(f"[⚠️] Error in update_memory: {e}")

# Also add this enhanced function for better integration
def get_user_context() -> Dict[str, Any]:
    """Get user context for personalized responses"""
    return {
        "title": memory.get_user_title(),
        "mood_preference": memory.get_mood_preference(),
        "name": memory.memory["user_preferences"].get("name"),
        "total_conversations": memory.memory["stats"]["total_conversations"],
        "favorite_features": memory.memory["stats"]["favorite_features"],
        "recent_interests": memory.memory["user_preferences"]["interests"]
    }