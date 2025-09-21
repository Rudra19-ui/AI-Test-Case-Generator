import json
import logging
import os
from typing import List, Dict, Any

from app.models import ComplianceSnippet
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for compliance snippets.
    
    This class manages the embedding and retrieval of compliance snippets
    for tagging test cases with relevant compliance references.
    """
    
    def __init__(self):
        """Initialize the vector store."""
        self.snippets: List[ComplianceSnippet] = []
        self.embeddings = None
        self.index = None
        self.model = None
        
        # Load the compliance snippets
        self._load_snippets()
        
        # Initialize the embedding model and index
        self._initialize_embeddings()
    
    def _load_snippets(self):
        """Load compliance snippets from the JSON file."""
        try:
            # Resolve the path relative to the current file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            snippets_path = os.path.join(base_dir, "sample_data", "compliance_snippets.json")
            
            if not os.path.exists(snippets_path):
                logger.warning(f"Compliance snippets file not found at {snippets_path}")
                return
            
            with open(snippets_path, 'r') as f:
                data = json.load(f)
            
            for item in data:
                self.snippets.append(ComplianceSnippet(**item))
            
            logger.info(f"Loaded {len(self.snippets)} compliance snippets")
        except Exception as e:
            logger.error(f"Error loading compliance snippets: {str(e)}")
    
    def _initialize_embeddings(self):
        """Initialize the embedding model and index."""
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            import faiss
            
            # Load the embedding model
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
            
            # Create embeddings for snippets
            if self.snippets:
                texts = [snippet.text for snippet in self.snippets]
                self.embeddings = self.model.encode(texts)
                
                # Create FAISS index
                dimension = self.embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(np.array(self.embeddings).astype('float32'))
                
                logger.info(f"Created FAISS index with {len(self.snippets)} vectors")
            else:
                logger.warning("No snippets available for embedding")
        except ImportError as e:
            logger.warning(f"Required packages not installed or incompatible: {str(e)}")
            logger.info("Continuing without vector embeddings - compliance tagging will be disabled")
        except Exception as e:
            logger.warning(f"Error initializing embeddings: {str(e)}")
            logger.info("Continuing without vector embeddings - compliance tagging will be disabled")
    
    async def query(self, text: str, top_k: int = 3) -> List[ComplianceSnippet]:
        """Query the vector store for relevant compliance snippets.
        
        Args:
            text: The query text (typically a requirement)
            top_k: Number of top results to return
            
        Returns:
            List of relevant ComplianceSnippet objects
        """
        if not self.snippets or self.index is None or self.model is None:
            logger.warning("Vector store not properly initialized")
            return []
        
        try:
            # Encode the query text
            query_embedding = self.model.encode([text])
            
            # Search the index
            distances, indices = self.index.search(np.array(query_embedding).astype('float32'), min(top_k, len(self.snippets)))
            
            # Get the relevant snippets
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.snippets):
                    snippet = self.snippets[idx]
                    # Add relevance score (convert distance to similarity)
                    relevance = 1.0 / (1.0 + distances[0][i])  # Convert distance to similarity score
                    results.append(ComplianceSnippet(
                        tag=snippet.tag,
                        text=snippet.text,
                        source=snippet.source,
                        relevance=relevance
                    ))
            
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            return []

# Create a singleton instance
vectorstore = VectorStore()