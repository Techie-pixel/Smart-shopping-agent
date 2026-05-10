"""
review_analyzer.py — Fake review detection using Groq LLM.
Analyzes rating patterns, review distribution, and text quality
to produce an authenticity score for each product.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_groq_client() -> Optional[Groq]:
    """Initialize Groq client with API key from environment."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY not set — review analysis will use heuristic fallback")
        return None
    return Groq(api_key=api_key)


def _heuristic_review_score(product: Dict) -> Dict:
    """
    Compute a heuristic-based review authenticity score when Groq is unavailable.
    Uses statistical patterns commonly associated with fake reviews.
    """
    score = 75  # Base score
    flags = []
    
    rating = product.get("rating")
    review_count = product.get("review_count")
    price = product.get("price", 0)

    # ── Pattern 1: Suspiciously perfect rating ──
    if rating and rating >= 4.8:
        score -= 15
        flags.append("Unusually high rating (≥4.8)")
    elif rating and rating >= 4.5:
        score -= 5
        flags.append("Very high rating")

    # ── Pattern 2: Too few reviews for a high rating ──
    if rating and rating >= 4.5 and review_count and review_count < 50:
        score -= 20
        flags.append("High rating with very few reviews")

    # ── Pattern 3: Rating-to-review ratio anomaly ──
    if review_count and review_count > 50000 and rating and rating >= 4.3:
        score -= 10
        flags.append("Extremely high review volume — possible incentivized reviews")

    # ── Pattern 4: Very cheap product with very high rating ──
    if price and price < 500 and rating and rating >= 4.5:
        score -= 10
        flags.append("Budget product with premium-level ratings")

    # ── Pattern 5: No reviews at all ──
    if not review_count or review_count == 0:
        score -= 25
        flags.append("No reviews available")

    # ── Pattern 6: Good middle-ground (organic signal) ──
    if rating and 3.8 <= rating <= 4.4 and review_count and review_count >= 100:
        score += 10
        flags.append("Natural rating distribution")

    # ── Pattern 7: Moderate review count (healthy sign) ──
    if review_count and 500 <= review_count <= 20000:
        score += 5

    score = max(20, min(100, score))

    return {
        "authenticity_score": score,
        "flags": flags,
        "verdict": _score_to_verdict(score),
        "method": "heuristic",
    }


def _score_to_verdict(score: int) -> str:
    """Convert numeric score to human-readable verdict."""
    if score >= 85:
        return "Highly Authentic"
    elif score >= 70:
        return "Likely Authentic"
    elif score >= 55:
        return "Mixed Signals"
    elif score >= 40:
        return "Suspicious"
    else:
        return "Likely Fake"


def analyze_single_product(product: Dict, client: Optional[Groq] = None) -> Dict:
    """
    Analyze a single product's review authenticity using Groq LLM.
    Falls back to heuristic analysis if Groq is unavailable.
    """
    if not client:
        return _heuristic_review_score(product)

    try:
        prompt = f"""You are a review authenticity expert. Analyze this product and estimate how authentic its reviews are.

Product: {product.get('name', 'Unknown')}
Price: ₹{product.get('price', 'N/A')}
Rating: {product.get('rating', 'N/A')}/5
Review Count: {product.get('review_count', 'N/A')}
Source: {product.get('source', 'Unknown')}
Specs: {', '.join(product.get('specs', []))}

Analyze for these fake review indicators:
1. Unnaturally high ratings (4.8+) with large review counts
2. Rating inconsistent with price bracket (too good for very cheap products)
3. Suspiciously round review counts
4. Known brands vs unknown brands (known brands typically have more authentic reviews)
5. Review count vs product age signals

Return ONLY valid JSON (no markdown, no code blocks):
{{"authenticity_score": <int 0-100>, "flags": [<list of concern strings>], "verdict": "<verdict string>"}}
"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a review authenticity analyst. Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        
        # Clean up response — remove markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        result = json.loads(raw)
        result["method"] = "groq_llm"
        result["verdict"] = result.get("verdict", _score_to_verdict(result.get("authenticity_score", 50)))
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Groq response for {product.get('name')}: {e}")
        return _heuristic_review_score(product)
    except Exception as e:
        logger.warning(f"Groq analysis failed for {product.get('name')}: {e}")
        return _heuristic_review_score(product)


def analyze_reviews(products: List[Dict]) -> List[Dict]:
    """
    Analyze all products for review authenticity.
    Adds 'review_analysis' key to each product dict.
    """
    client = _get_groq_client()
    
    for product in products:
        analysis = analyze_single_product(product, client)
        product["review_analysis"] = analysis
        logger.info(
            f"📊 {product.get('name', 'Unknown')[:40]}: "
            f"Score={analysis['authenticity_score']}, "
            f"Verdict={analysis['verdict']}"
        )

    return products
