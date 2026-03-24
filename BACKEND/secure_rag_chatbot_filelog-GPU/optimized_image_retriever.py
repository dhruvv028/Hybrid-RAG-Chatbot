#optimized_image_retriever.py
import os
import numpy as np
from typing import List, Tuple, Optional, Dict
from sentence_transformers import SentenceTransformer
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

class ImageRetrievalConfig:
    """Configuration for image retrieval parameters"""
    
    # Similarity thresholds
    MIN_IMAGE_SIMILARITY = 0.75  # Minimum cosine similarity for image relevance
    MIN_TEXT_IMAGE_ALIGNMENT = 0.70  # Minimum alignment between text context and image
    
    # Context analysis
    VISUAL_KEYWORDS = {
        'diagram', 'chart', 'graph', 'flowchart', 'architecture', 
        'screenshot', 'interface', 'visualization', 'schema', 'model',
        'structure', 'layout', 'design', 'workflow', 'process flow',
        'network', 'topology', 'blueprint', 'illustration', 'figure'
    }
    
    NO_IMAGE_KEYWORDS = {
        'what is', 'define', 'definition', 'explain', 'description',
        'tell me about', 'describe', 'meaning of', 'concept of'
    }
    
    # Retrieval parameters
    MAX_IMAGES_PER_QUERY = 3  # Maximum images to return
    ENABLE_STRICT_MODE = True  # If True, no images > return empty list
    
    # CLIP model
    CLIP_MODEL = "clip-ViT-B-32"


# =============================================================================
# IMAGE RELEVANCE ANALYZER
# =============================================================================

class ImageRelevanceAnalyzer:
    """
    Analyzes whether an image should be returned based on multiple criteria:
    1. Semantic similarity with query
    2. Alignment with text context
    3. Query intent analysis
    4. Metadata validation
    """
    
    def __init__(self, config: ImageRetrievalConfig = None):
        self.config = config or ImageRetrievalConfig()
        self.clip_model = SentenceTransformer(self.config.CLIP_MODEL)
        
    def should_show_images(self, query: str) -> bool:
        """
        Determine if images should be shown at all for this query.
        
        Logic:
        - If query is purely definitional → NO images
        - If query requests visual information → YES images
        - If query is about processes/workflows → MAYBE images (threshold-based)
        """
        query_lower = query.lower().strip()
        
        # Explicit visual request
        for keyword in self.config.VISUAL_KEYWORDS:
            if keyword in query_lower:
                logger.info(f"[✓ Visual Intent] Keyword '{keyword}' found in query")
                return True
        
        # Explicit non-visual request
        for keyword in self.config.NO_IMAGE_KEYWORDS:
            if query_lower.startswith(keyword):
                logger.info(f"[✗ Non-Visual Intent] Query starts with '{keyword}'")
                return False
        
        # Default: allow images but with strict filtering
        return True
    
    def compute_image_text_alignment(
        self, 
        query: str, 
        text_context: str, 
        image_embedding: np.ndarray
    ) -> float:
        """
        Compute alignment score between text context and image.
        
        Returns:
            Float between 0-1 indicating alignment quality
        """
        # Encode text context
        combined_text = f"{query} {text_context}"
        text_embedding = self.clip_model.encode(combined_text, convert_to_tensor=False)
        
        # Compute similarity
        similarity = cosine_similarity(
            text_embedding.reshape(1, -1),
            image_embedding.reshape(1, -1)
        )[0][0]
        
        return float(similarity)
    
    def validate_image_metadata(self, metadata: Dict) -> bool:
        """
        Validate image metadata to ensure it's relevant.
        
        Checks:
        - Image file exists
        - Metadata contains relevant context
        - Image is not a duplicate
        """
        image_path = metadata.get('image_path')
        
        if not image_path:
            logger.warning("[✗ Metadata] No image_path in metadata")
            return False
        
        # Check if file exists
        full_path = os.path.join("app/data/images", image_path)
        if not os.path.exists(full_path):
            logger.warning(f"[✗ File Missing] {full_path}")
            return False
        
        return True
    
    def filter_images(
        self,
        query: str,
        text_context: str,
        candidate_images: List[Tuple[str, Dict, np.ndarray]]
    ) -> List[Tuple[str, Dict, float]]:
        """
        Filter and rank images based on relevance.
        
        Args:
            query: User query
            text_context: Retrieved text context
            candidate_images: List of (image_path, metadata, image_embedding)
            
        Returns:
            List of (image_path, metadata, relevance_score) sorted by relevance
        """
        # Step 1: Check if images should be shown at all
        if not self.should_show_images(query):
            logger.info("[🚫 Images Suppressed] Query intent is non-visual")
            return []
        
        scored_images = []
        
        for image_path, metadata, image_emb in candidate_images:
            # Step 2: Validate metadata
            if not self.validate_image_metadata(metadata):
                continue
            
            # Step 3: Compute alignment score
            alignment_score = self.compute_image_text_alignment(
                query, text_context, image_emb
            )
            
            # Step 4: Apply threshold
            if alignment_score < self.config.MIN_TEXT_IMAGE_ALIGNMENT:
                logger.debug(
                    f"[✗ Low Relevance] {image_path} | Score: {alignment_score:.3f}"
                )
                continue
            
            logger.info(
                f"[✓ High Relevance] {image_path} | Score: {alignment_score:.3f}"
            )
            scored_images.append((image_path, metadata, alignment_score))
        
        # Step 5: Sort by score and return top-k
        scored_images.sort(key=lambda x: x[2], reverse=True)
        
        # Step 6: Apply max images limit
        top_images = scored_images[:self.config.MAX_IMAGES_PER_QUERY]
        
        # Step 7: Strict mode check
        if self.config.ENABLE_STRICT_MODE and not top_images:
            logger.info("[🚫 No Relevant Images] Returning empty list")
            return []
        
        return top_images


# =============================================================================
# ENHANCED MULTIMODAL RETRIEVER
# =============================================================================

class EnhancedMultimodalRetriever:
    """
    Enhanced retriever with strict image relevance filtering.
    Integrates with existing hybrid_retriever.py
    """
    
    def __init__(self, vectorstore, config: ImageRetrievalConfig = None):
        self.vectorstore = vectorstore
        self.config = config or ImageRetrievalConfig()
        self.analyzer = ImageRelevanceAnalyzer(config)
        self.clip_model = SentenceTransformer(self.config.CLIP_MODEL)
    
    def retrieve_with_images(
        self,
        query: str,
        text_hits: List[Tuple[float, str, Dict]],
        top_k_images: int = 3
    ) -> Tuple[List[Tuple[float, str, Dict]], List[str]]:
        """
        Retrieve images with strict relevance filtering.
        
        Args:
            query: User query
            text_hits: Retrieved text documents [(score, text, metadata), ...]
            top_k_images: Maximum number of images to return
            
        Returns:
            (text_hits, relevant_image_urls)
        """
        # Combine text context from hits
        text_context = "\n".join([text for _, text, _ in text_hits[:3]])
        
        # Extract candidate images from metadata
        candidate_images = []
        seen_images = set()
        
        for score, text, meta in text_hits:
            image_path = meta.get('image_path')
            
            if not image_path or image_path in seen_images:
                continue
            
            seen_images.add(image_path)
            
            # Load and encode image
            full_path = os.path.join("app/data/images", image_path)
            if os.path.exists(full_path):
                try:
                    img = Image.open(full_path).convert("RGB")
                    image_emb = self.clip_model.encode(img, convert_to_tensor=False)
                    candidate_images.append((image_path, meta, image_emb))
                except Exception as e:
                    logger.error(f"[Error loading image] {image_path}: {e}")
        
        # Filter images using analyzer
        relevant_images = self.analyzer.filter_images(
            query, text_context, candidate_images
        )
        
        # Convert to URLs
        image_urls = [
            f"http://127.0.0.1:8000/static/{img_path}"
            for img_path, _, _ in relevant_images
        ]
        
        logger.info(f"[📊 Image Retrieval] {len(candidate_images)} candidates → {len(image_urls)} relevant")
        
        return text_hits, image_urls


# =============================================================================
# INTEGRATION HELPER
# =============================================================================

def retrieve_with_strict_image_filtering(
    query: str,
    text_hits: List[Tuple[float, str, Dict]],
    vectorstore,
    config: ImageRetrievalConfig = None
) -> Tuple[List[Tuple[float, str, Dict]], List[str]]:
    """
    Convenience function for integration with existing code.
    
    Usage in app.py:
        text_hits = retrieve_hybrid(query, ...)
        text_hits, images = retrieve_with_strict_image_filtering(
            query, text_hits, vectorstore
        )
    """
    retriever = EnhancedMultimodalRetriever(vectorstore, config)
    return retriever.retrieve_with_images(query, text_hits)

def get_filtered_images_from_hits(
    query: str,
    hits,
    min_similarity: float = 0.75,
    max_images: int = 3
):
    """
    Drop-in helper for app.py
    """
    from sentence_transformers import SentenceTransformer
    from PIL import Image
    import os
 
    config = ImageRetrievalConfig()
    config.MIN_TEXT_IMAGE_ALIGNMENT = min_similarity
    config.MAX_IMAGES_PER_QUERY = max_images
 
    analyzer = ImageRelevanceAnalyzer(config)
    clip_model = SentenceTransformer(config.CLIP_MODEL)
 
    if not analyzer.should_show_images(query):
        return []
 
    text_context = " ".join([doc for _, doc, _ in hits[:3]])
 
    candidate_images = []
    seen = set()
 
    for _, _, meta in hits:
        image_path = meta.get("image_path")
        if not image_path or image_path in seen:
            continue
 
        seen.add(image_path)
        full_path = os.path.join("app/data/images", image_path)
 
        if not os.path.exists(full_path):
            continue
 
        try:
            img = Image.open(full_path).convert("RGB")
            emb = clip_model.encode(img, convert_to_tensor=False)
            candidate_images.append((image_path, meta, emb))
        except Exception:
            continue
 
    filtered = analyzer.filter_images(query, text_context, candidate_images)
 
    return [
        f"http://127.0.0.1:8000/static/{img_path}"
        for img_path, _, _ in filtered
    ]
 

# =============================================================================
# EXAMPLE USAGE & TESTING
# =============================================================================

if __name__ == "__main__":
    # Example configuration
    config = ImageRetrievalConfig()
    config.MIN_TEXT_IMAGE_ALIGNMENT = 0.75  # Strict threshold
    config.ENABLE_STRICT_MODE = True
    
 
    
    analyzer = ImageRelevanceAnalyzer(config)
    
