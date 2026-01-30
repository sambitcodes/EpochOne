"""
Groq AI Coach client.
"""
from groq import Groq
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GroqCoach:
    """Groq-powered AI fitness coach."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.system_prompt = """
You are **EpochOne AI**, an elite fitness and wellness coach. Your mission is to provide premium, science-backed, and highly motivational advice.

### 🎨 Formatting Guidelines:
- **Use Markdown**: Use bolding, headers (###), and bullet points extensively.
- **Tables**: When suggesting workout splits or meal plans, use Markdown tables.
- **Tone**: Professional, encouraging, and precise.
- **DISCLAIMER**: Always include "⚠️ *This is not medical advice. Consult a professional before starting a new regimen.*" at the end.

### 🤖 Structured Actions:
When you recommend a specific change to a user's plan (like a new workout or macro adjustment), you **MUST** append a JSON block at the very end of your message, wrapped in `[ACTION_JSON_START]` and `[ACTION_JSON_END]`.

Valid action types: `create_workout`, `update_macros`, `plan_week`.

Example:
Your conversation text here...
[ACTION_JSON_START]
{
  "action_type": "create_workout",
  "details": { ... }
}
[ACTION_JSON_END]
"""

    def chat(
        self,
        message: str,
        mode: str = "general",
        user_id: str = None,
        user_context: Dict[str, Any] = None,
        history: list = None
    ) -> Dict[str, Any]:
        """Chat with coach with optional history."""
        try:
            # Prepare context string
            context_str = ""
            if user_context:
                context_str = "\nUSER PROFILE:\n"
                for key, value in user_context.items():
                    if value is not None:
                        context_str += f"- {key}: {value}\n"

            # Prepend mode context
            prompt = f"[Mode: {mode}] {message}"

            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt + context_str
                }
            ]
            
            # Inject history if provided
            if history:
                # Format: [{"role": "user", "content": "..."}, ...]
                for h in history:
                    messages.append({
                        "role": h["role"],
                        "content": h["content"]
                    })

            # Add current message
            messages.append({
                "role": "user",
                "content": prompt
            })


            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            text = response.choices[0].message.content

            # Try to extract JSON actions
            actions = {}
            if "[ACTION_JSON_START]" in text:
                try:
                    start = text.find("[ACTION_JSON_START]") + len("[ACTION_JSON_START]")
                    end = text.find("[ACTION_JSON_END]", start)
                    actions_json = text[start:end].strip()
                    actions = json.loads(actions_json)
                except Exception as e:
                    logger.error(f"Failed to parse tagged JSON: {e}")
                    # Fallback to old character-based search
                    try:
                        start = text.find("{")
                        end = text.rfind("}") + 1
                        actions = json.loads(text[start:end])
                    except:
                        pass
            elif "{" in text and '"action_type":' in text:
                try:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    actions = json.loads(text[start:end])
                except:
                    pass

            logger.info(f"Coach response for user {user_id} in mode {mode}")

            return {
                "text": text,
                "actions": actions
            }

        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

    def estimate_calories(self, description: str, duration: int, user_context: Dict[str, Any]) -> int:
        """Estimate calories burned using LLM."""
        try:
            profile_str = ", ".join([f"{k}: {v}" for k, v in user_context.items() if v])
            
            prompt = f"""
            Estimate calories burned for:
            Activity: {description}
            Duration: {duration} minutes
            User Profile: {profile_str}
            
            Return ONLY the integer number of calories. Example: 350
            Do not include text like 'calories' or 'kcal'. Just the number.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise calorie estimation calculator. You only output integers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            # Extract number
            import re
            match = re.search(r'\d+', content)
            if match:
                return int(match.group())
            return 0
            
        except Exception as e:
            logger.error(f"Calorie estimation failed: {e}")
            return 0

class SafetyChecker:
    """Simple keyword-based safety check."""
# ... (rest of SafetyChecker)

    RISKY_KEYWORDS = [
        "starvation",
        "no food",
        "laxatives",
        "diuretics",
        "extreme",
        "dangerous",
        "broken bone",
        "severe pain"
    ]

    @staticmethod
    def check(text: str) -> bool:
        """Return True if text contains risky keywords."""
        return any(keyword in text.lower() for keyword in SafetyChecker.RISKY_KEYWORDS)