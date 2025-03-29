import asyncio
import random


async def analyze_text(text: str) -> dict:
    await asyncio.sleep(random.uniform(1, 3))
    text_lower = text.lower()

    if any(word in text_lower for word in ["error", "exception", "failed"]):
        category = "critical"
        confidence = random.uniform(0.7, 0.95)
    elif any(word in text_lower for word in ["warning", "attention", "careful"]):
        category = "warning"
        confidence = random.uniform(0.6, 0.9)
    else:
        category = "info"
        confidence = random.uniform(0.8, 0.99)

    return {
        "category": category,
        "confidence": confidence,
        "keywords": random.sample(text.split(), min(3, len(text.split())))
    }
