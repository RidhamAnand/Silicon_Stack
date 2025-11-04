"""
Configuration management for the AI Customer Support Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Grok API
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    GROK_API_BASE = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    GROK_MODEL = "grok-beta"
    
    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 dimension
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "customer-support-faqs")
    
    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "customer_support")
    
    # Application Settings
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    SENTIMENT_THRESHOLD = float(os.getenv("SENTIMENT_THRESHOLD", "-0.6"))
    TOP_K_RESULTS = 3
    
    # Flask
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # MCP Servers
    ORDER_MCP_PORT = int(os.getenv("ORDER_MCP_PORT", "3001"))
    USER_MCP_PORT = int(os.getenv("USER_MCP_PORT", "3002"))
    TICKET_MCP_PORT = int(os.getenv("TICKET_MCP_PORT", "3003"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = []
        
        if not cls.GROK_API_KEY:
            required.append("GROK_API_KEY")
        if not cls.PINECONE_API_KEY:
            required.append("PINECONE_API_KEY")
        if not cls.MONGODB_URI:
            required.append("MONGODB_URI")
        
        if required:
            raise ValueError(f"Missing required environment variables: {', '.join(required)}")
        
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        return True

# Export config instance
config = Config()
