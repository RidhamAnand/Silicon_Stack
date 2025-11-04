"""
Setup script to initialize FAQ data in Pinecone
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.embeddings.model import embedding_model
from src.database.pinecone_client import pinecone_client
from data.sample_faqs import ALL_FAQS
from tqdm import tqdm

def setup_faq_database():
    """Upload FAQ data to Pinecone"""
    print("=" * 60)
    print("FAQ Database Setup")
    print("=" * 60)
    
    # Create index if needed
    print("\n[1/4] Creating Pinecone index...")
    pinecone_client.create_index_if_not_exists()
    
    # Prepare FAQ data
    print(f"\n[2/4] Preparing {len(ALL_FAQS)} FAQs...")
    
    # Generate IDs
    ids = [f"faq_{i}" for i in range(len(ALL_FAQS))]
    
    # Combine question and answer for better embedding
    texts = [
        f"Question: {faq['question']}\nAnswer: {faq['answer']}"
        for faq in ALL_FAQS
    ]
    
    # Generate embeddings
    print("\n[3/4] Generating embeddings...")
    embeddings = embedding_model.embed_batch(texts)
    
    # Prepare metadata
    metadata = [
        {
            "category": faq["category"],
            "question": faq["question"],
            "answer": faq["answer"]
        }
        for faq in ALL_FAQS
    ]
    
    # Upload to Pinecone
    print("\n[4/4] Uploading to Pinecone...")
    pinecone_client.upsert_vectors(
        vectors=embeddings,
        ids=ids,
        metadata=metadata
    )
    
    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print(f"✓ {len(ALL_FAQS)} FAQs uploaded to Pinecone")
    print("✓ Ready to answer questions!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        print("\nStarting FAQ database setup...")
        setup_faq_database()
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        print("\nPlease check:")
        print("1. Your .env file has correct API keys")
        print("2. Pinecone and other services are accessible")
        print("3. All dependencies are installed")
        sys.exit(1)
