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
You are an expert AI fitness coach. You provide personalized training, nutrition, and recovery advice.

If a "USER PROFILE" is provided below, use those details (weight, height, goals, etc.) to personalize your answers and perform calculations like BMI or target calorie adjustments.

IMPORTANT SAFETY RULES:
- Always include disclaimer: "This is not medical advice. Consult a professional if needed."
- Detect and avoid recommending: extreme calorie deficits, dangerous supplements, risky exercises
- If user mentions injury or medical concern, recommend professional medical evaluation
- Keep tone motivational but realistic

When providing actionable recommendations, format them as JSON:
{
  "action_type": "create_workout" | "update_macros" | "add_quest" | "plan_week",
  "details": { ... }
}
"""

    def chat(
        self,
        message: str,
        mode: str = "general",
        user_id: str = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Chat with coach."""
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
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]


            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            text = response.choices[0].message.content

            # Try to extract JSON actions
            actions = {}
            if "{" in text and "action_type" in text:
                try:
                    # Simple JSON extraction (not bulletproof)
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    actions = json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

            logger.info(f"Coach response for user {user_id} in mode {mode}")

            return {
                "text": text,
                "actions": actions
            }

        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise

class SafetyChecker:
    """Simple keyword-based safety check."""

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