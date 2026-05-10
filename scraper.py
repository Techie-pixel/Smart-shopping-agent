"""
scraper.py — Product scraper powered by SerpAPI (Google Shopping).
Replaces the brittle BeautifulSoup approach for guaranteed clean results without anti-bot 403 errors.
"""

import os
import re
import logging
import urllib.parse
from typing import List, Dict, Optional
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

def _extract_price(price_val) -> Optional[float]:
    """Extract numeric price from a string or float."""
    if isinstance(price_val, (int, float)):
        return float(price_val)
    if not price_val:
        return None
    cleaned = re.sub(r"[^\d.]", "", str(price_val).replace(",", ""))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def extract_specs(title: str, snippet: str) -> List[str]:
    """Extract simple specs/tags from title and snippet."""
    combined = (title + " " + snippet).lower()
    possible_tags = [
        "wireless", "bluetooth", "rgb", "anti-slip", "extended xl", "fast charging", 
        "anc", "waterproof", "ipx7", "ip55", "noise cancelling", "mechanical", "oled", "120hz",
        "5g", "ssd", "ips", "1080p", "4k"
    ]
    caps = re.findall(r'\b\d+(?:gb|tb)\b', combined)
    tags = []
    for t in possible_tags:
        if t in combined:
            tags.append(t.title())
    for c in set(caps):
        tags.append(c.upper())
    return list(set(tags))[:5]

def scrape_products(query: str, max_per_source: int = 8) -> List[Dict]:
    """
    Scrape products using SerpAPI's Google Shopping engine.
    Filters for Amazon and Flipkart sources to keep the comparison clean.
    """
    if not SERPAPI_KEY:
        logger.error("🚨 SERPAPI_API_KEY not found in environment!")
        return get_demo_products(query)

    logger.info(f"🔍 Fetching products via SerpAPI for: {query}")
    all_products = []

    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            logger.error(f"SerpAPI Error: {results['error']}")
            return get_demo_products(query)

        shopping_results = results.get("shopping_results", [])
        logger.info(f"Found {len(shopping_results)} total shopping results from SerpAPI")

        amazon_count = 0
        flipkart_count = 0

        for item in shopping_results:
            source = item.get("source", "")
            
            # We specifically want to compare Amazon and Flipkart
            if "amazon" in source.lower():
                if amazon_count >= max_per_source: continue
                source_clean = "Amazon"
                amazon_count += 1
            elif "flipkart" in source.lower():
                if flipkart_count >= max_per_source: continue
                source_clean = "Flipkart"
                flipkart_count += 1
            else:
                # If we don't have enough results, accept other trusted stores as fallbacks
                if len(all_products) < 5:
                    source_clean = source
                else:
                    continue

            # SerpAPI usually provides extracted_price, but we fallback to price string
            price = _extract_price(item.get("extracted_price") or item.get("price"))
            if not price:
                continue

            title = item.get("title", "Unknown Product")
            snippet = item.get("snippet", "")
            if not snippet and "description" in item:
                snippet = item["description"]
            
            # Construct direct store search links
            if source_clean == "Amazon":
                url = f"https://www.amazon.in/s?k={urllib.parse.quote(title)}"
            elif source_clean == "Flipkart":
                url = f"https://www.flipkart.com/search?q={urllib.parse.quote(title)}"
            else:
                url = item.get("link", item.get("product_link", "#"))

            product = {
                "name": title,
                "price": price,
                "rating": item.get("rating"),
                "review_count": item.get("reviews"),
                "specs": extract_specs(title, snippet),
                "description": snippet,
                "url": url,
                "thumbnail": item.get("thumbnail", ""),
                "source": source_clean,
            }
            all_products.append(product)

    except Exception as e:
        logger.error(f"Exception during SerpAPI request: {e}")
        return get_demo_products(query)

    # Deduplicate by name
    seen_names = set()
    unique_products = []
    for p in all_products:
        normalized = p["name"].lower().strip()[:60] if p["name"] else ""
        if normalized and normalized not in seen_names:
            seen_names.add(normalized)
            unique_products.append(p)

    logger.info(f"🏁 SerpAPI returned {len(unique_products)} valid unique products")
    
    if not unique_products:
        logger.warning("No valid products found via SerpAPI, falling back to demo data.")
        return get_demo_products(query)

    return unique_products


# ═══════════════════════════════════════════════
#  DEMO / FALLBACK DATA (used when API fails/limits hit)
# ═══════════════════════════════════════════════

def get_demo_products(product_type: str) -> List[Dict]:
    """
    Return realistic demo product data when live scraping fails.
    This ensures the UI always has something to display.
    """
    demos = {
        "headphones": [
            {"name": "boAt Rockerz 450 Bluetooth Headphones", "price": 1299, "rating": 4.1, "review_count": 84523, "specs": ["40mm Drivers", "15H Battery", "Bluetooth 5.0"], "description": "High-quality wireless headphones with deep bass.", "url": "https://www.flipkart.com", "thumbnail": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/p/r/z/rockerz-450-boat-original-imagr4exyzzgggzh.jpeg?q=70", "source": "Flipkart"},
            {"name": "JBL Tune 520BT Wireless Headphones", "price": 2999, "rating": 4.3, "review_count": 12045, "specs": ["Pure Bass Sound", "57H Battery", "Bluetooth 5.3"], "description": "Experience pure bass with the JBL Tune wireless headphones.", "url": "https://www.amazon.in", "thumbnail": "https://m.media-amazon.com/images/I/61kWB+uzR2L._SX522_.jpg", "source": "Amazon"},
            {"name": "Sony WH-CH520 Wireless Headphones", "price": 3490, "rating": 4.4, "review_count": 8932, "specs": ["30mm Drivers", "50H Battery", "Lightweight 147g"], "description": "Digital sound enhancement engine restores compressed music.", "url": "https://www.flipkart.com", "thumbnail": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/x/j/0/wh-ch520-sony-original-imagqys8tqzbhcqh.jpeg?q=70", "source": "Flipkart"},
            {"name": "Oneplus Nord Buds 2R TWS Earbuds", "price": 2299, "rating": 4.2, "review_count": 15678, "specs": ["12.4mm Titanium", "38H Battery", "Dolby Atmos"], "description": "True wireless earbuds with 12.4mm dynamic drivers.", "url": "https://www.amazon.in", "thumbnail": "https://m.media-amazon.com/images/I/511T+jN--7L._SX522_.jpg", "source": "Amazon"},
            {"name": "realme Buds Air 5 Pro ANC Earbuds", "price": 3499, "rating": 4.3, "review_count": 6543, "specs": ["50dB ANC", "38H Battery", "LDAC Codec"], "description": "Active noise cancellation up to 50dB with LDAC support.", "url": "https://www.flipkart.com", "thumbnail": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/t/v/y/-original-imagsszyy7wgn7xz.jpeg?q=70", "source": "Flipkart"},
        ],
        "laptop": [
            {"name": "Lenovo IdeaPad Slim 3 Intel i5 12th Gen", "price": 42990, "rating": 4.2, "review_count": 3456, "specs": ["8GB RAM", "512GB SSD", "15.6\" FHD"], "description": "Thin and light laptop with Intel Core i5 processor.", "url": "https://www.flipkart.com", "source": "Flipkart"},
            {"name": "HP 15s Intel Core i3 12th Gen", "price": 33990, "rating": 4.1, "review_count": 7890, "specs": ["8GB RAM", "512GB SSD", "Windows 11"], "description": "Everyday laptop designed for productivity and entertainment.", "url": "https://www.amazon.in", "source": "Amazon"},
            {"name": "ASUS Vivobook 15 AMD Ryzen 5", "price": 38990, "rating": 4.3, "review_count": 2345, "specs": ["8GB RAM", "512GB SSD", "Radeon Graphics"], "description": "Powerful laptop with AMD Ryzen 5 processor and Radeon graphics.", "url": "https://www.flipkart.com", "source": "Flipkart"},
        ],
        "smartphone": [
            {"name": "Samsung Galaxy M34 5G (6GB/128GB)", "price": 14999, "rating": 4.2, "review_count": 45678, "specs": ["Exynos 1280", "6000mAh", "50MP Camera"], "description": "5G smartphone with massive 6000mAh battery and Super AMOLED display.", "url": "https://www.flipkart.com", "source": "Flipkart"},
            {"name": "Redmi Note 13 5G (6GB/128GB)", "price": 13999, "rating": 4.1, "review_count": 34567, "specs": ["Dimensity 6080", "5000mAh", "108MP Camera"], "description": "Ultra-clear 108MP camera and fast Dimensity 6080 processor.", "url": "https://www.amazon.in", "source": "Amazon"},
        ],
    }

    query_lower = product_type.lower()
    for key in demos:
        if key in query_lower:
            return demos[key]

    return demos.get("headphones", [])
