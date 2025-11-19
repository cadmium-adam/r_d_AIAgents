"""
Content generation functionality for descriptions and reviews.
Supports Ollama LLM integration with fallback templates.
"""

import random
import time
import re
from typing import Dict, Any, Optional
from ollama import Client

from .base_generator import BaseGenerator


class ContentGenerator(BaseGenerator):
    """Handles text content generation for products and reviews."""

    def __init__(
        self,
        use_llm: bool = True,
        ollama_host: str = "http://localhost:11434",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.use_llm = use_llm
        self.ollama_client = None
        self.description_cache = {}

        # Initialize Ollama client if requested
        if self.use_llm:
            try:
                self.ollama_client = Client(host=ollama_host)
                # Test connection
                self.ollama_client.list()
                print("✓ Ollama connection established")
            except Exception as e:
                print(f"⚠ Warning: Could not connect to Ollama ({e}). Using fallback descriptions.")
                self.use_llm = False

    def clean_unicode_characters(self, text: str) -> str:
        """Remove unicode characters, emojis, and special symbols from text."""
        # Remove emojis and unicode symbols
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # Remove specific unicode escape sequences
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def generate_llm_description(
        self,
        product_name: str,
        category: str,
        brand: str,
        features: Dict[str, Any] = None,
    ) -> str:
        """Generate realistic product description using Ollama LLM."""
        if not self.use_llm or not self.ollama_client:
            return self.generate_fallback_description(product_name, category, brand)

        # Check cache first
        features_str = str(sorted(features.items())) if features else ""
        cache_key = f"{product_name}_{category}_{brand}_{features_str}"
        if cache_key in self.description_cache:
            return self.description_cache[cache_key]

        try:
            # Build feature information for the prompt
            features_text = ""
            if features:
                feature_list = [f"{k}: {v}" for k, v in features.items() if v]
                if feature_list:
                    features_text = f"\nKey Features: {', '.join(feature_list)}"

            prompt = f"""Write a realistic, engaging product description for an e-commerce website. 

Product: {product_name}
Category: {category}
Brand: {brand}
{features_text}

Requirements:
- 150-200 characters maximum
- Focus on key features and benefits mentioned above
- Use professional, marketing-friendly language
- Include relevant keywords for search
- Make it specific to the product type and its features
- Highlight the most important features naturally

Write only the description, no additional text."""

            response = self.ollama_client.chat(
                model="mistral",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional product copywriter for e-commerce.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            description = response.message.content.strip()
            
            # Remove unicode characters and emojis
            description = self.clean_unicode_characters(description)

            # Cache the result
            self.description_cache[cache_key] = description

            # Add small delay to be respectful to the LLM
            time.sleep(0.1)

            return description

        except Exception as e:
            print(f"⚠ LLM description generation failed: {e}. Using fallback.")
            return self.generate_fallback_description(product_name, category, brand)

    def generate_fallback_description(
        self, product_name: str, category: str, brand: str
    ) -> str:
        """Generate fallback description when LLM is unavailable."""
        templates = {
            "Electronics": [
                f"High-performance {product_name.split()[-1].lower()} from {brand}. Advanced technology meets sleek design for exceptional user experience.",
                f"Professional-grade {product_name.split()[-1].lower()} featuring cutting-edge innovation. Perfect for work and entertainment.",
                f"Premium {product_name.split()[-1].lower()} with superior build quality. Designed for performance and reliability.",
            ],
            "Clothing": [
                f"Stylish and comfortable {product_name.split()[-1].lower()} from {brand}. Premium materials and perfect fit for any occasion.",
                f"Trendy {product_name.split()[-1].lower()} designed for comfort and style. Quality craftsmanship meets modern fashion.",
                f"Versatile {product_name.split()[-1].lower()} perfect for everyday wear. Durable construction and timeless design.",
            ],
            "Books": [
                f"Engaging {product_name.split()[-1].lower()} that captivates readers. Well-researched content and compelling narrative.",
                f"Comprehensive {product_name.split()[-1].lower()} perfect for learning and entertainment. Expert insights and clear presentation.",
                f"Must-read {product_name.split()[-1].lower()} offering valuable knowledge. Thoughtfully written and expertly crafted.",
            ],
            "Home & Garden": [
                f"Essential {product_name.split()[-1].lower()} for modern homes. Quality construction and practical design for everyday use.",
                f"Durable {product_name.split()[-1].lower()} built to last. Combines functionality with aesthetic appeal.",
                f"Reliable {product_name.split()[-1].lower()} that enhances your living space. Professional quality for home use.",
            ],
            "Sports": [
                f"High-performance {product_name.split()[-1].lower()} for athletes and fitness enthusiasts. Built for durability and optimal results.",
                f"Professional-quality {product_name.split()[-1].lower()} designed for serious training. Superior materials and ergonomic design.",
                f"Essential {product_name.split()[-1].lower()} for active lifestyles. Engineered for performance and comfort.",
            ],
        }

        category_templates = templates.get(category, templates["Electronics"])
        description = random.choice(category_templates)
        return self.clean_unicode_characters(description)

    def generate_llm_review(
        self,
        product_name: str,
        category: str,
        rating: int,
        features: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """Generate realistic product review using Ollama LLM."""
        if not self.use_llm or not self.ollama_client:
            return self.generate_fallback_review(product_name, category, rating)

        try:
            # Build feature information for the prompt
            features_text = ""
            if features:
                feature_list = [f"{k}: {v}" for k, v in features.items() if v]
                if feature_list:
                    features_text = f"\nProduct Features: {', '.join(feature_list)}"

            # Rating-based context
            rating_context = {
                1: "very disappointed and frustrated",
                2: "disappointed but trying to be fair",
                3: "neutral, has mixed feelings",
                4: "satisfied and positive",
                5: "extremely happy and enthusiastic",
            }

            prompt = f"""Write a realistic product review for an e-commerce website.

Product: {product_name}
Category: {category}
Rating: {rating}/5 stars
Reviewer mood: {rating_context[rating]}{features_text}

Requirements:
- Write both a review title (5-8 words) and review comment (30-60 words)
- Make it sound like a real customer wrote it
- Mention specific features when relevant
- Match the tone to the star rating
- Use natural, conversational language
- Include personal experience details

Format your response exactly like this:
TITLE: [review title here]
COMMENT: [review comment here]"""

            response = self.ollama_client.chat(
                model="mistral",
                messages=[
                    {
                        "role": "system",
                        "content": "You are writing authentic customer reviews. Be specific and natural.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.message.content.strip()

            # Parse the response
            lines = content.split("\n")
            title = ""
            comment = ""

            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith("TITLE:"):
                    title = line_stripped.replace("TITLE:", "").strip()
                elif line_stripped.startswith("COMMENT:"):
                    comment = line_stripped.replace("COMMENT:", "").strip()

            # Fallback if parsing fails
            if not title or not comment:
                return self.generate_fallback_review(product_name, category, rating)

            # Clean unicode characters from review content
            title = self.clean_unicode_characters(title)
            comment = self.clean_unicode_characters(comment)

            time.sleep(0.1)  # Be respectful to the LLM

            return {"title": title, "comment": comment}

        except Exception as e:
            print(f"⚠ LLM review generation failed: {e}. Using fallback.")
            return self.generate_fallback_review(product_name, category, rating)

    def generate_fallback_review(
        self, product_name: str, category: str, rating: int
    ) -> Dict[str, str]:
        """Generate fallback review when LLM is unavailable."""
        product_type = product_name.split()[-1].lower()

        if rating >= 4:
            titles = [
                f"Great {product_type}!",
                f"Love this {product_type}",
                f"Excellent quality {product_type}",
                f"Very satisfied with {product_type}",
                f"Outstanding {product_type}",
            ]
            comments = [
                f"Great {product_type}! Exactly what I was looking for.",
                f"Excellent quality and fast shipping. Highly recommend!",
                f"Love this {product_type}. Works perfectly and looks great.",
                f"Very satisfied with this purchase. Good value for money.",
                f"Outstanding {product_type}. Will definitely buy again.",
            ]
        elif rating == 3:
            titles = [
                f"Good {product_type}, but...",
                f"Average {product_type}",
                f"Decent {product_type} for the price",
                f"Okay {product_type}",
            ]
            comments = [
                f"Good {product_type}, but could be better.",
                f"Average quality. Does the job but nothing special.",
                f"Okay purchase. Some issues but generally fine.",
                f"Decent {product_type} for the price.",
            ]
        else:
            titles = [
                f"Disappointed with {product_type}",
                f"Not what I expected",
                f"Poor quality {product_type}",
                f"Would not recommend",
            ]
            comments = [
                f"Not what I expected. Poor quality.",
                f"Disappointed with this purchase.",
                f"{product_type} doesn't match description.",
                f"Would not recommend. Had several issues.",
            ]

        return {"title": random.choice(titles), "comment": random.choice(comments)}