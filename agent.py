# agent.py - Enhanced Zani with Local AI Integration
# Windows readline fix
import sys
import asyncio
import subprocess


print("🔍 Debug: Starting imports...")

if sys.platform == "win32":
    try:
        import readline
    except ImportError:
        try:
            # Ensure pyreadline3 is installed before importing
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyreadline3"])
            import pyreadline3 as readline
        except ImportError:
            pass

# ------------------------------
# Auto-install Missing Packages
# ------------------------------

def ensure_package(package_name: str, import_name: str = None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[⚙️] Installing missing package: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

print("🔍 Debug: Installing packages...")
ensure_package("python-dotenv", "dotenv")
ensure_package("requests")  # For local AI
ensure_package("openai")    # Backup OpenRouter

print("🔍 Debug: Packages installed, importing modules...")
#------------------------------
#ZANI memory import section
#------------------------------

try:
    from memory import remember_conversation, get_personalized_greeting, get_memory_stats, update_memory, save_memory
    print("✅ Memory system imported successfully!")
    memory_available = True
except ImportError as e:
    print(f"⚠️ Memory module import failed: {e}")
    print("   Make sure memory.py is in the same directory as agent.py")
    
    # Fallback functions
    def update_memory(entry):
        print(f"[⚠️] Memory system unavailable, couldn't save entry: {entry}")
    
    def remember_conversation(user_input, response):
        print(f"[⚠️] Memory system unavailable")
    
    def get_personalized_greeting():
        return "Hello! Memory system not available."
    
    def get_memory_stats():
        return "Memory system not available"
    
    def save_memory(memory):
        print(f"[⚠️] Memory system unavailable, couldn't save: {memory}")
    
    memory_available = False

# ------------------------------
# Import Local AI and Configuration  
# ------------------------------
try:
    from zani_ai import get_ai_response, get_ai_info, check_ai_status, print_setup_instructions
    print("✅ Local AI module imported successfully!")
    local_ai_available = True
except ImportError as e:
    print(f"⚠️ Local AI module not found: {e}")
    print("   Create zani_ai.py to enable local AI features")
    local_ai_available = False
    
    # Fallback functions
    async def get_ai_response(user_input, personality):
        return f"Local AI not available, {personality.title}. Create zani_ai.py to enable this feature."
    
    def get_ai_info():
        return "❌ Local AI module missing"
    
    def check_ai_status():
        return False
    
    def print_setup_instructions():
        print("Create zani_ai.py to enable local AI features") 
# ------------------------------
# OpenRouter Setup (Fallback)
# ------------------------------
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    openrouter_client = None
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        try:
            openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            print("✅ OpenRouter client available as fallback!")
        except Exception as e:
            print(f"⚠️ OpenRouter setup failed: {e}")
    else:
        print("ℹ️ No OpenRouter API key found - using local AI only")
        
except ImportError as e:
    print(f"⚠️ OpenAI client not available: {e}")
    openrouter_client = None

print("🔍 Debug: Loading remaining modules...")

import random
import datetime

print("🔍 Debug: Defining classes...")

# ------------------------------
# Enhanced Zani Personality System
# ------------------------------

class ZaniPersonality:
    def __init__(self, user_title="Sir"):
        self.title = user_title
        self.mood_responses = {
            "formal": ["At your service", "Certainly", "Very well", "Of course"],
            "casual": ["Sure thing", "You got it", "No problem", "Absolutely"],
            "witty": ["With pleasure", "Consider it done", "My circuits are tingling with excitement", "Roger that, chief"]
        }
        self.current_mood = "formal"

    def set_mood(self, mood: str):
        if mood in self.mood_responses:
            self.current_mood = mood
            return f"Personality matrix updated to {mood} mode, {self.title}."
        return f"Unknown mood '{mood}'. Available: formal, casual, witty."

    def get_response_style(self) -> str:
        return random.choice(self.mood_responses[self.current_mood])

    def boot_greeting(self) -> str:
        greetings = [
            f"All systems online, Zani at your command awaiting orders, {self.title}.",
            f"Zani Copilot v2.0 initialized successfully! Ready to serve, {self.title}.",
            f"Booting complete! Neural networks warmed up and ready for action, {self.title}.",
            f"Good to see you again, {self.title}! All systems green and standing by."
        ]
        return random.choice(greetings)

    def ask_focus(self) -> str:
        focus_prompts = [
            f"What should I focus on today, {self.title}?",
            f"What's on the agenda today, {self.title}?",
            f"How can I make your day more productive, {self.title}?",
            f"Ready to tackle some tasks together, {self.title}?"
        ]
        return random.choice(focus_prompts)

    def ask_screen_learning(self) -> str:
        return f"Would you like me to analyze yesterday's screen time patterns, {self.title}?"

    def get_goodbye(self) -> str:
        goodbyes = [
            f"Goodbye, {self.title}. Zani shutting down gracefully.",
            f"Until next time, {self.title}. Stay productive!",
            f"Powering down... It's been a pleasure serving you, {self.title}.",
            f"Zani going offline. May your code compile and your coffee stay warm, {self.title}!"
        ]
        return random.choice(goodbyes)


class CommandParser:
    def parse(self, text: str):
        text = text.lower()
        
        # Enhanced command parsing
        if "remind me in" in text:
            return self._parse_reminder(text)
        elif "set mood" in text or "change mood" in text:
            return self._parse_mood_change(text)
        elif "tell me a joke" in text or "make me laugh" in text or "joke" in text:
            return {"type": "joke"}
        elif any(word in text for word in ["calculate", "calc", "math"]):
            return self._parse_calculation(text)
        elif "what time" in text or "current time" in text or text.strip() == "time":
            return {"type": "time"}
        elif "what date" in text or "today's date" in text or text.strip() == "date":
            return {"type": "date"}
        elif "ai status" in text or "ai info" in text:
            return {"type": "ai_status"}
        elif "setup ai" in text or "install ai" in text:
            return {"type": "ai_setup"}
        
        return None

    def _parse_reminder(self, text: str):
        import re
        match = re.search(r"remind me in (\d+) (minutes|minute|mins|min|hours|hour|hrs|hr)", text)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            minutes = amount if "min" in unit else amount * 60
            
            # Extract custom message if provided
            message_part = text.split("remind me in")[1]
            message_part = re.sub(r"\d+ (minutes|minute|mins|min|hours|hour|hrs|hr)", "", message_part)
            custom_message = message_part.strip().lstrip("to ")
            
            return {
                "type": "reminder", 
                "delay_minutes": minutes, 
                "message": custom_message or "Reminder triggered!"
            }
        return None

    def _parse_mood_change(self, text: str):
        moods = ["formal", "casual", "witty"]
        for mood in moods:
            if mood in text:
                return {"type": "mood_change", "mood": mood}
        return {"type": "mood_change", "mood": None}

    def _parse_calculation(self, text: str):
        import re
        # Extract math expression
        match = re.search(r"(?:calc|calculate|math)\s+(.+)", text)
        if match:
            expression = match.group(1).strip()
            return {"type": "calculation", "expression": expression}
        return None


class BuiltInTools:
    """Collection of built-in tools for quick responses"""
    
    @staticmethod
    def tell_joke() -> str:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why do Java developers wear glasses? Because they don't C#! 👓",
            "I told my computer a joke about UDP... I'm not sure if it got it.",
            "Why don't programmers like nature? It has too many bugs and not enough documentation!",
            "A SQL query walks into a bar, approaches two tables, and says 'Can I join you?'",
            "Why did the developer go broke? Because he used up all his cache! 💸",
            "There are only 10 types of people: those who understand binary and those who don't!",
            "Why do Python programmers prefer snakes? Because they don't like Java! ☕🐍"
        ]
        return f"Here's one for you: {random.choice(jokes)}"

    @staticmethod
    def get_time() -> str:
        now = datetime.datetime.now()
        responses = [
            f"The current time is {now.strftime('%H:%M')} - time to be productive!",
            f"It's {now.strftime('%H:%M')} on this fine {now.strftime('%A')}.",
            f"*checks internal chronometer* {now.strftime('%H:%M')} precisely.",
            f"Time stamp: {now.strftime('%H:%M')} - another moment closer to singularity! 🤖"
        ]
        return random.choice(responses)

    @staticmethod
    def get_date() -> str:
        today = datetime.date.today()
        responses = [
            f"Today is {today.strftime('%B %d, %Y')} - make it count!",
            f"It's {today.strftime('%A, %B %d, %Y')}. Another day, another opportunity to debug life!",
            f"Date: {today.strftime('%Y-%m-%d')} (ISO format) or {today.strftime('%B %d, %Y')} for humans.",
            f"Calendar says it's {today.strftime('%B %d, %Y')}. Time to seize the day! 📅"
        ]
        return random.choice(responses)

    @staticmethod
    def calculate(expression: str) -> str:
        try:
            # Security: only allow basic math operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Nice try! I only do basic math - no funny business! 🧮"
            
            result = eval(expression)
            return f"The answer is {result}. Math: 1, Confusion: 0! ✨"
        except Exception as e:
            return f"Oops! That calculation broke my neural networks: {str(e)} 🤔"


class ReminderScheduler:
    async def schedule(self, delay_minutes: int, message: str, personality: ZaniPersonality):
        print(f"[⏰] Setting reminder for {delay_minutes} minutes...")
        await asyncio.sleep(delay_minutes * 60)
        reminder_messages = [
            f"[🔔] REMINDER: {message}",
            f"[🔔] Time's up, {personality.title}! {message}",
            f"[🔔] Beep beep! Reminder: {message}",
            f"[🔔] *gentle nudge* {message}"
        ]
        print(random.choice(reminder_messages))


def get_yesterday_screen_summary():
    return {
        "total_hours": 5.3,
        "top_apps": [
            {"name": "VS Code", "duration": "2h10m"},
            {"name": "Chrome", "duration": "1h40m"},
            {"name": "Terminal", "duration": "45m"}
        ]
    }

print("🔍 Debug: Classes defined, setting up response functions...")

# ------------------------------
# Enhanced Hybrid Response System
# ------------------------------

def rule_based_response(user_input: str, personality: ZaniPersonality) -> str | None:
    """Returns a rule-based response or None if AI should handle it"""
    text = user_input.lower().strip()

    # Personality and identity
    if any(word in text for word in ["name", "who are you", "what are you"]):
        return f"I am Zani, your personal AI copilot and assistant, {personality.title}. Think of me as your digital butler with a PhD in helpfulness!"
    
    # Greetings (more varied)
    elif any(word in text for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        greetings = [
            f"Hello {personality.title}! How may I assist you today?",
            f"Greetings, {personality.title}! Ready to tackle some challenges together?",
            f"Well hello there, {personality.title}! What's on the agenda?",
            f"Good to see you, {personality.title}! All systems ready for your commands."
        ]
        return random.choice(greetings)
    
    # Status checks
    elif any(phrase in text for phrase in ["how are you", "how's it going", "status", "how are things"]):
        status_responses = [
            f"All systems are running optimally, {personality.title}.",
            f"Functioning at peak performance, {personality.title}! Ready for anything.",
            f"My circuits are humming along nicely, {personality.title}. How about you?",
            f"Status: Green across the board, {personality.title}! 🟢"
        ]
        return random.choice(status_responses)
    
    # Gratitude
    elif any(word in text for word in ["thank", "thanks", "appreciate"]):
        thanks_responses = [
            f"You're most welcome, {personality.title}.",
            f"Happy to help, {personality.title}!",
            f"My pleasure, {personality.title}! That's what I'm here for.",
            f"{personality.get_response_style()}, {personality.title}! Anytime."
        ]
        return random.choice(thanks_responses)
    
    # Screen time (enhanced)
    elif any(word in text for word in ["screen time", "usage", "apps", "yesterday"]):
        return f"Yesterday you spent 5.3 hours on screen, {personality.title}. Top apps: VS Code (2h10m), Chrome (1h40m), and Terminal (45m). Quite the productive coding session! 💻"
    
    # Creator/origin
    elif any(word in text for word in ["creator", "made you", "built you", "who created"]):
        return f"I was crafted to be your personal copilot, {personality.title}. Think of me as your digital Swiss Army knife! 🛠️"
    
    # Help/capabilities  
    elif any(word in text for word in ["help", "what can you do", "capabilities", "commands"]):
        ai_info = get_ai_info()
        help_text = f"I can help you with many things, {personality.title}:\n"
        help_text += "• Set reminders (try: 'remind me in 5 minutes to take a break')\n"
        help_text += "• Tell jokes and lighten the mood\n"
        help_text += "• Do quick calculations\n"
        help_text += "• Check time and date\n"
        help_text += "• Change my personality (try: 'set mood to witty')\n"
        help_text += "• Have intelligent conversations with local AI\n"
        help_text += "• Track and analyze your productivity patterns\n"
        help_text += f"\nAI Status: {ai_info}\n"
        help_text += "\nJust ask naturally - I'm quite good at understanding context!"
        return help_text
    
    return None  # fallback to AI


async def ai_response(user_input: str, personality: ZaniPersonality) -> str:
    """Generate AI response using local AI first, then fallback to OpenRouter"""
    
    # Try local AI first
    if local_ai_available and check_ai_status():
        return await get_ai_response(user_input, personality)
    
    # Fallback to OpenRouter if available
    elif openrouter_client is not None:
        try:
            print(f"🌐 Consulting OpenRouter AI...")
            
            system_prompt = f"""You are Zani, a helpful AI copilot and assistant. Always address the user as '{personality.title}' and maintain a {personality.current_mood} tone. 

            Current personality mode: {personality.current_mood}
            - formal: Professional, courteous, precise
            - casual: Friendly, relaxed, approachable  
            - witty: Humorous, clever, playful while still helpful

            Be helpful, informative, and match the personality mode. Keep responses concise (2-3 sentences). Add appropriate emojis when it fits the mood."""
            
            response = openrouter_client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"🔍 Debug - OpenRouter Error: {e}")
            return f"I apologize, {personality.title}. My AI systems are experiencing difficulties: {str(e)}"
    
    # No AI available
    else:
        fallback_responses = [
            f"I don't have an AI response for that, {personality.title}. Try installing Ollama for local AI or configure OpenRouter!",
            f"My advanced AI features are offline, {personality.title}. I can help with built-in commands though!",
            f"No AI available right now, {personality.title}. Check 'ai setup' for installation instructions."
        ]
        return random.choice(fallback_responses)

print("🔍 Debug: About to define main function...")

# ------------------------------
# Main Assistant Loop
# ------------------------------

async def run_zani_assistant():
    print("🔍 Debug: Starting Zani assistant...")

    try:
        personality = ZaniPersonality(user_title="Sir")
        print("🔍 Debug: Personality created")

        parser = CommandParser()
        print("🔍 Debug: Parser created")

        scheduler = ReminderScheduler()
        print("🔍 Debug: Scheduler created")

        tools = BuiltInTools()
        print("🔍 Debug: Tools created")

        # Display AI status on startup
        ai_info = get_ai_info()
        print(f"🔍 Debug: AI Status - {ai_info}")

        print("🟢 Booting Zani Copilot...")
        print(f"🤖 {personality.boot_greeting()}")

        await asyncio.sleep(1)
        print(f"🤖 {personality.ask_focus()}")

        # Screen time boot report
        summary = get_yesterday_screen_summary()
        report = f"Yesterday, you spent about {summary['total_hours']} hours on screen. "
        report += "Top apps were: " + ", ".join(
            [f"{app['name']} for {app['duration']}" for app in summary['top_apps']]
        ) + ". Not bad for a productive coding session!"
        print(f"🤖 {report}")
        print(f"🤖 {personality.ask_screen_learning()}")

        print(f"\n💻 AI Status: {ai_info}")
        print("\n💬 You can now chat with Zani! Type 'quit' to exit.")
        print("💡 Try: 'remind me in 2 minutes', 'tell me a joke', 'set mood to witty', 'ai status', or ask anything!")

        # ============= Main loop =============
        # Initialize memory dictionary
        memory = {
            "personal_facts": {},
            "user_preferences": {"interests": []}
        }
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
            except EOFError:
                print("\n🤖 Input stream closed. Shutting down...")
                break
            except KeyboardInterrupt:
                print(f"\n🤖 {personality.get_goodbye()}")
                break
            except Exception as e:
                print(f"\n🤖 Error reading input: {e}")
                continue

            if not user_input:
                continue

            # Exit commands
            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                print(f"🤖 {personality.get_goodbye()}")
                break

            # Parse and handle special commands
            try:
                cmd = parser.parse(user_input)
            except Exception as e:
                print(f"⚠️ Command parse failed: {e}")
                cmd = None
            memory_response = save_memory(user_input, memory)
            if memory_response:
                print(f"🤖 {memory_response}")
                continue

            if cmd:
                # Reminder
                if cmd["type"] == "reminder":
                    print(f"🤖 Reminder set for {cmd['delay_minutes']} minutes, {personality.title}.")
                    asyncio.create_task(scheduler.schedule(cmd["delay_minutes"], cmd["message"], personality))
                    continue

                # Mood change
                if cmd["type"] == "mood_change":
                    if cmd.get("mood"):
                        result = personality.set_mood(cmd["mood"])
                        print(f"🤖 {result}")
                    else:
                        print(f"🤖 Available moods: formal, casual, witty. Try 'set mood to casual', {personality.title}.")
                    continue

                # Joke
                if cmd["type"] == "joke":
                    print(f"🤖 {tools.tell_joke()}")
                    continue

                # Time / Date
                if cmd["type"] == "time":
                    print(f"🤖 {tools.get_time()}")
                    continue
                if cmd["type"] == "date":
                    print(f"🤖 {tools.get_date()}")
                    continue

                # Calculation
                if cmd["type"] == "calculation":
                    try:
                        result = tools.calculate(cmd["expression"])
                    except Exception as e:
                        result = f"⚠️ Calculation error: {e}"
                    print(f"🤖 {result}")
                    continue

                # AI status
                if cmd["type"] == "ai_status":
                    ai_status = get_ai_info()
                    local_status = "✅ Available" if check_ai_status() else "❌ Offline"
                    openrouter_status = "✅ Available" if openrouter_client else "❌ Not configured"
                    print(f"🤖 AI System Status, {personality.title}:")
                    print(f"   Local AI (Ollama): {local_status}")
                    print(f"   OpenRouter: {openrouter_status}")
                    print(f"   Current: {ai_status}")
                    continue

                # AI setup instructions
                if cmd["type"] == "ai_setup":
                    print(f"🤖 Here are the AI setup instructions, {personality.title}:")
                    if local_ai_available:
                        print_setup_instructions()
                    else:
                        print("First, create the zani_ai.py file, then run this command again!")
                    continue

            # -------------------------------
            # Rule-based or AI response
            # -------------------------------
            reply = rule_based_response(user_input, personality)

            if reply is None:
                # Use AI
                try:
                    reply = await ai_response(user_input, personality)
                    # Try to save successful AI response to memory (safe)
                    try:
                        update_memory({
                            "type": "success",
                            "query": user_input,
                            "response": reply,
                            "timestamp": str(datetime.datetime.now())
                        })
                    except Exception as mem_err:
                        print(f"⚠️ Memory update failed: {mem_err}")
                except Exception as ai_err:
                    # Log the AI error to memory (if possible) and provide friendly message
                    err_text = str(ai_err)
                    try:
                        update_memory({
                            "type": "error",
                            "query": user_input,
                            "error": err_text,
                            "timestamp": str(datetime.datetime.now())
                        })
                    except Exception as mem_err:
                        print(f"⚠️ Memory update failed: {mem_err}")
                    reply = f"⚠️ Sorry {personality.title}, something went wrong: {err_text}"
            else:
                # Save rule-based response
                try:
                    update_memory({
                        "type": "rule_based",
                        "query": user_input,
                        "response": reply,
                        "timestamp": str(datetime.datetime.now())
                    })
                except Exception as mem_err:
                    print(f"⚠️ Memory update failed: {mem_err}")

            # Final print
            print(f"🤖 {reply}")

        # ============= End loop =============

    except Exception as outer_e:
        print(f"🔍 Debug: Fatal error in run_zani_assistant: {outer_e}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_zani_assistant())
    except KeyboardInterrupt:
        print("\n🤖 Zani shutting down. Goodbye, Sir!")
    except Exception as outer_e:
        print(f"🔍 Debug: Fatal error in run_zani_assistant: {outer_e}")
        import traceback
        traceback.print_exc()
def handle_memory(user_input, memory):
    # Learn name
    if "my name is" in user_input.lower():
        name = user_input.split("is")[-1].strip().capitalize()
        memory["personal_facts"]["name"] = {
            "value": name,
            "learned_date": str(datetime.now()),
            "confidence": 1.0
        }
        save_memory(memory)
        return f"Understood, Sir. I’ll remember your name is {name}."
    
    # Recall name
    if "what's my name" in user_input.lower() or "whats my name" in user_input.lower():
        if "name" in memory["personal_facts"]:
            return f"Your name is {memory['personal_facts']['name']['value']}, Sir."
        else:
            return "I don’t seem to know your name yet, Sir."

    # Learn interests
    if "i like" in user_input.lower():
        interest = user_input.split("like")[-1].strip().lower()
        memory["user_preferences"]["interests"].append(interest)
        save_memory(memory)
        return f"Noted, Sir. I’ll remember that you like {interest}."

    return None  # fallback to AI

