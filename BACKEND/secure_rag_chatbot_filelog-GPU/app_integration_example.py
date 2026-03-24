"""
Updated app.py with Optimized Image Retrieval
==============================================
Integrates strict image relevance filtering to prevent off-topic images.
"""
from logging import config
import os
import logging as logger
from hybrid_retriever import retrieve_hybrid
from config import Config
from generator import generate_answer
from typing import List,Tuple, Dict

Config = Config()

# Add this import at the top of your existing app.py
from optimized_image_retriever import (
    ImageRetrievalConfig,
    ImageRelevanceAnalyzer,
    EnhancedMultimodalRetriever,
    get_filtered_images_from_hits
)

# ---------------- UPDATED Bot Processing Function ---------------- #
def process_bot_with_optimized_images(query: str, bot_type: str):
    """
    Enhanced version of process_bot() with strict image filtering.
    
    Changes from original:
    1. Uses ImageRelevanceAnalyzer to determine if images should be shown
    2. Applies cosine similarity threshold filtering
    3. Validates image-text alignment before returning
    4. Returns empty list if no highly relevant images found
    """
    logger.info(f"[BOT-{bot_type}] Query: {query}")
    hits = retrieve_hybrid(query, use_hyde=config.use_hyde, bot=bot_type)
    logger.info(f"[BOT-{bot_type}] Hits: {len(hits)}")

    if not hits:
        return "No relevant answer found in the knowledge base.", []

    # Initialize image retrieval components
    img_config = ImageRetrievalConfig()
    img_config.MIN_TEXT_IMAGE_ALIGNMENT = 0.75  # Strict threshold
    img_config.ENABLE_STRICT_MODE = True  # No images better than wrong images
    
    analyzer = ImageRelevanceAnalyzer(img_config)
    
    # Build context
    context_parts = []
    text_context = ""
    
    for _, doc, meta in hits:
        context_parts.append(doc)
        text_context += doc + " "
       # logger.info(f"[META DEBUG] {meta}")

        if bot_type == "B":
            reason = meta.get("Reason", "").strip()
            resolution = meta.get("Resolution", "").strip()
            if reason:
                context_parts.append(f"Reason: {reason}")
            if resolution:
                context_parts.append(f"Resolution: {resolution}")

    # Step 1: Check if images should be shown at all
    if not analyzer.should_show_images(query):
      #  logger.info("[🚫 Images Suppressed] Query is non-visual")
        relevant_images = []
    else:
        # Step 2: Collect and filter candidate images
        from sentence_transformers import SentenceTransformer
        clip_model = SentenceTransformer(img_config.CLIP_MODEL)
        
        candidate_images = []
        seen_images = set()
        
        for _, doc, meta in hits:
            image_path = meta.get("image_path")
            
            if not image_path or image_path in seen_images:
                continue
            
            seen_images.add(image_path)
            
            # Validate file exists
            full_path = os.path.join("app/data/images", image_path)
            if os.path.exists(full_path):
                try:
                    from PIL import Image
                    img = Image.open(full_path).convert("RGB")
                    image_emb = clip_model.encode(img, convert_to_tensor=False)
                    candidate_images.append((image_path, meta, image_emb))
                except Exception as e:
                    logger.error(f"[Image Load Error] {image_path}: {e}")
        
        # Step 3: Filter images with strict relevance checking
        filtered_images = analyzer.filter_images(query, text_context, candidate_images)
        
        # Step 4: Convert to URLs
        relevant_images = [
            f"http://127.0.0.1:8000/static/{img_path}"
            for img_path, _, score in filtered_images
        ]
        
        logger.info(
            f"[📊 Image Filtering] {len(candidate_images)} candidates → "
            f"{len(relevant_images)} relevant (threshold={img_config.MIN_TEXT_IMAGE_ALIGNMENT})"
        )

    # ----------------- Truth source collection -----------------
    source_links = set()
    for _, _, meta in hits:
        pdf_file = meta.get("source", None)
        page_no = meta.get("page", None)
        if pdf_file:
            link = f"http://127.0.0.1:8000/static/knowledge/{pdf_file}"
            if page_no:
                link += f"#page={page_no}"
            display_text = f"{pdf_file}"
            if page_no:
                display_text += f" - Page {page_no}"
            source_links.add(f"[{display_text}]({link})")

    if not context_parts:
        return "No relevant answer found in the knowledge base.", []

    # ----------------- Generate answer -----------------
    context = "\n\n".join(context_parts)
    answer = generate_answer(query, context, bot_type)

    # Append truth sources
    if source_links:
        answer += "\n\n**Sources:** " + ", ".join(source_links)

    return answer, relevant_images


# ---------------- ALTERNATIVE: Drop-in Replacement Function ---------------- #
def get_filtered_images_from_hits(
    query: str,
    hits: List[Tuple[float, str, Dict]],
    min_similarity: float = 0.75,
    max_images: int = 3
) -> List[str]:
    """
    Drop-in replacement for image extraction logic.
    Can be used in your existing process_bot() function.
    
    Args:
        query: User query
        hits: Retrieved documents from hybrid_retriever
        min_similarity: Minimum cosine similarity threshold
        max_images: Maximum number of images to return
        
    Returns:
        List of image URLs (empty if no relevant images)
    """
    from optimized_image_retriever import ImageRetrievalConfig, ImageRelevanceAnalyzer
    from sentence_transformers import SentenceTransformer
    from PIL import Image
    import numpy as np
    
    # Setup
    config = ImageRetrievalConfig()
    config.MIN_TEXT_IMAGE_ALIGNMENT = min_similarity
    config.MAX_IMAGES_PER_QUERY = max_images
    
    analyzer = ImageRelevanceAnalyzer(config)
    clip_model = SentenceTransformer(config.CLIP_MODEL)
    
    # Check if images should be shown
    if not analyzer.should_show_images(query):
        return []
    
    # Build text context
    text_context = " ".join([doc for _, doc, _ in hits[:3]])
    
    # Collect candidate images
    candidate_images = []
    seen_images = set()
    
    for _, doc, meta in hits:
        image_path = meta.get("image_path")
        
        if not image_path or image_path in seen_images:
            continue
        
        seen_images.add(image_path)
        full_path = os.path.join("app/data/images", image_path)
        
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path).convert("RGB")
                image_emb = clip_model.encode(img, convert_to_tensor=False)
                candidate_images.append((image_path, meta, image_emb))
            except Exception as e:
                logger.error(f"[Image Error] {image_path}: {e}")
    
    # Filter with strict relevance
    filtered = analyzer.filter_images(query, text_context, candidate_images)
    
    # Convert to URLs
    return [
        f"http://127.0.0.1:8000/static/{img_path}"
        for img_path, _, _ in filtered
    ]


# ---------------- USAGE EXAMPLE IN YOUR EXISTING CODE ---------------- #
"""
To integrate into your existing app.py, replace lines 85-106 with:

    context_parts = []
    
    for _, doc, meta in hits:
        context_parts.append(doc)
        logger.info(f"[META DEBUG] {meta}")

        if bot_type == "B":
            reason = meta.get("Reason", "").strip()
            resolution = meta.get("Resolution", "").strip()
            if reason:
                context_parts.append(f"Reason: {reason}")
            if resolution:
                context_parts.append(f"Resolution: {resolution}")

    # Use optimized image filtering instead of naive extraction
    relevant_images = get_filtered_images_from_hits(
        query=query,
        hits=hits,
        min_similarity=0.75,  # Adjust this threshold as needed
        max_images=3
    )
"""
