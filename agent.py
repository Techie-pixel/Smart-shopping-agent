"""
agent.py — Main AI agent orchestrator for Smart Shopping.
Handles: query parsing (via Groq), product scraping, review analysis,
and value-for-money ranking.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from groq import Groq

from scraper import scrape_products, get_demo_products
from review_analyzer import analyze_reviews

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  GROQ CLIENT
# ═══════════════════════════════════════════════

def _get_groq_client() -> Optional[Groq]:
    """Get a Groq client instance."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)


# ═══════════════════════════════════════════════
#  QUERY PARSING (Groq LLM)
# ═══════════════════════════════════════════════

def parse_query(user_query: str) -> Dict:
    """
    Use Groq LLM to extract structured shopping intent from natural language.
    Returns: { product_type, budget, search_query, features }
    """
    client = _get_groq_client()

    # Fallback: simple keyword extraction if Groq is unavailable
    if not client:
        return _fallback_parse(user_query)

    try:
        prompt = f"""You are a shopping assistant. Extract the user's shopping intent from their query.

User query: "{user_query}"

Return ONLY valid JSON (no markdown, no code fences):
{{
    "product_type": "<category like headphones, laptop, smartphone, etc.>",
    "budget": <max budget as integer in INR, or null if not mentioned>,
    "search_query": "<optimized search string for e-commerce sites>",
    "features": [<list of specific features/requirements mentioned>]
}}

Rules:
- If no budget mentioned, set to null
- search_query should be concise and optimized for e-commerce search
- product_type should be a single general category word
- features should capture specific requirements (brand, specs, use case)
"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Extract shopping intent. Return ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=250,
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        parsed = json.loads(raw)
        logger.info(f"🧠 Parsed query: {parsed}")
        return parsed

    except Exception as e:
        logger.warning(f"Groq parse failed: {e}, using fallback parser")
        return _fallback_parse(user_query)


def _fallback_parse(query: str) -> Dict:
    """
    Simple keyword-based query parser as fallback when Groq is unavailable.
    """
    import re

    query_lower = query.lower()

    # Extract budget
    budget = None
    budget_patterns = [
        r"(?:under|below|within|budget|max|upto|up to|less than)\s*(?:rs\.?|₹|inr)?\s*([\d,]+)",
        r"(?:rs\.?|₹|inr)\s*([\d,]+)",
        r"([\d,]+)\s*(?:rs|₹|rupees|inr|budget)",
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, query_lower)
        if match:
            budget = int(match.group(1).replace(",", ""))
            break

    # Extract product type
    product_keywords = [
        "headphones", "earphones", "earbuds", "headset",
        "laptop", "notebook",
        "smartphone", "phone", "mobile",
        "tablet", "ipad",
        "smartwatch", "watch", "band",
        "camera", "dslr",
        "speaker", "soundbar",
        "keyboard", "mouse",
        "monitor", "tv", "television",
        "refrigerator", "fridge",
        "washing machine",
        "air conditioner", "ac",
        "microwave",
        "trimmer", "shaver",
        "power bank",
        "router", "wifi",
    ]

    product_type = "product"
    for keyword in product_keywords:
        if keyword in query_lower:
            product_type = keyword
            break

    # Build search query (remove budget-related words)
    search_query = re.sub(
        r"(?:under|below|within|budget|max|upto|up to|less than|find|search|show|get|me|best|good|i want|i need|please|can you|recommend)\s*",
        "",
        query_lower,
    ).strip()
    search_query = re.sub(r"(?:rs\.?|₹|inr)\s*[\d,]+", "", search_query).strip()
    search_query = re.sub(r"\s+", " ", search_query).strip()

    if not search_query or len(search_query) < 3:
        search_query = product_type

    return {
        "product_type": product_type,
        "budget": budget,
        "search_query": search_query,
        "features": [],
    }


# ═══════════════════════════════════════════════
#  VALUE-FOR-MONEY RANKING
# ═══════════════════════════════════════════════

def compute_value_score(product: Dict, budget: Optional[int] = None) -> float:
    """
    Compute a composite value-for-money score (0–100) for a product.
    Factors: price vs budget fit, rating, review authenticity, review volume.
    """
    score = 0.0
    price = product.get("price", 0)
    rating = product.get("rating")
    review_count = product.get("review_count", 0)
    auth_score = product.get("review_analysis", {}).get("authenticity_score", 70)

    # ── Budget Fit (30 points max) ──
    if budget and price:
        if price <= budget:
            # Closer to budget = more value (using most of the budget)
            utilization = price / budget
            if utilization >= 0.7:
                score += 30  # Sweet spot — good utilization
            elif utilization >= 0.4:
                score += 25
            else:
                score += 15  # Very cheap relative to budget
        else:
            # Over budget — penalize proportionally
            overshoot = (price - budget) / budget
            score += max(0, 15 - (overshoot * 30))
    elif price:
        score += 20  # No budget specified — neutral

    # ── Rating Quality (30 points max) ──
    if rating:
        # Penalize below 3.5, reward above 3.5
        r_val = float(rating)
        r_score = ((r_val - 3.0) / 2.0) * 30 if r_val > 3.0 else 0
        score += max(0, min(30, r_score))

    # ── Review Authenticity (25 points max) ──
    score += (auth_score / 100.0) * 25

    # ── Review Volume (15 points max) ──
    if review_count:
        if review_count >= 10000:
            score += 15
        elif review_count >= 1000:
            score += 12
        elif review_count >= 100:
            score += 8
        elif review_count >= 10:
            score += 4
        else:
            score += 1

    return round(min(100, max(0, score)), 1)


def rank_products(products: List[Dict], budget: Optional[int] = None) -> List[Dict]:
    """
    Rank products by value-for-money score.
    Adds 'match_score' to each product and sorts descending.
    """
    for product in products:
        product["match_score"] = compute_value_score(product, budget)

    # Sort by match_score descending
    products.sort(key=lambda p: p["match_score"], reverse=True)
    return products


def filter_top_5_with_groq(products: List[Dict], query: str) -> List[Dict]:
    """
    Use Groq API to pick exactly the 5 best products from the given list.
    """
    client = _get_groq_client()
    if not client or len(products) <= 5:
        return products[:5]

    try:
        simple_products = []
        for i, p in enumerate(products[:15]): # limit to top 15 to avoid large prompts
            simple_products.append({
                "id": i,
                "name": p.get("name"),
                "price": p.get("price"),
                "rating": p.get("rating"),
                "source": p.get("source"),
            })

        prompt = f"""You are an expert shopping assistant. Here are products scraped for the query "{query}".
Select exactly the top 5 best products based on value for money, brand reputation, ratings, and price.
Return ONLY a JSON list of the 'id's of the selected 5 products, e.g., [0, 3, 4, 1, 7].

Products:
{json.dumps(simple_products, indent=2)}
"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant. Return only a JSON array of integers."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=100,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        # Some times LLMs prefix with "json" inside the block
        if raw.startswith("json"):
            raw = raw[4:].strip()

        selected_ids = json.loads(raw)
        
        filtered = []
        for pid in selected_ids:
            if isinstance(pid, int) and 0 <= pid < len(products):
                if products[pid] not in filtered:
                    filtered.append(products[pid])
                
        # Fill up to 5 if needed
        for p in products:
            if len(filtered) >= 5:
                break
            if p not in filtered:
                filtered.append(p)
                
        return filtered[:5]

    except Exception as e:
        logger.warning(f"Groq filter failed: {e}, falling back to top 5")
        return products[:5]



# ═══════════════════════════════════════════════
#  MAIN AGENT PIPELINE
# ═══════════════════════════════════════════════

def run_agent(user_query: str) -> Tuple[Dict, List[Dict]]:
    """
    Execute the full smart shopping agent pipeline:
    1. Parse query → extract product type + budget
    2. Scrape products from Flipkart + Amazon
    3. Analyze reviews for authenticity
    4. Rank by value for money
    5. Return parsed intent + ranked products

    Args:
        user_query: Natural language shopping query

    Returns:
        (parsed_intent, ranked_products)
    """
    logger.info(f"Agent pipeline started for: '{user_query}'")

    # Step 1: Parse the query
    parsed = parse_query(user_query)
    logger.info(f"Intent: type={parsed['product_type']}, budget={parsed['budget']}")

    # Step 2: Scrape products
    products = scrape_products(parsed["search_query"], max_per_source=8)
    if not products:
        logger.warning("Live scraping returned 0 results — falling back to demo data")
        products = get_demo_products(parsed["product_type"])

    # Step 3: Filter by budget (if specified)
    if parsed["budget"]:
        budget = parsed["budget"]
        # Keep products within 120% of budget (slight flexibility)
        products = [p for p in products if p["price"] and p["price"] <= budget * 1.2]
        if not products:
            # If too restrictive, fall back to all products
            logger.warning("Budget filter too strict — showing all results")
            products = scrape_products(parsed["search_query"], max_per_source=8)
            if not products:
                products = get_demo_products(parsed["product_type"])

    # Step 4: Analyze reviews
    products = analyze_reviews(products)

    # Step 5: Rank by value
    products = rank_products(products, parsed.get("budget"))
    
    # Step 6: Filter top 5 using Groq API
    products = filter_top_5_with_groq(products, user_query)

    logger.info(f"Agent pipeline complete — {len(products)} products ranked")
    return parsed, products
