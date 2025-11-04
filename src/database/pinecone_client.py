"""
Pinecone vector database client
"""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
from src.config.settings import config
import time

class PineconeClient:
    """Client for Pinecone vector database"""

    def __init__(self):
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index_name = config.PINECONE_INDEX_NAME
        self.index = None

    def ensure_index(self):
        """Ensure the index is initialized and ready"""
        if self.index is None:
            try:
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                print(f"Error connecting to index {self.index_name}: {e}")
                print("Make sure the index exists and your API key is correct.")
                raise

    def create_index_if_not_exists(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=config.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            print("Index created successfully!")
        else:
            print(f"Index {self.index_name} already exists")

        self.index = self.pc.Index(self.index_name)

    def upsert_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict]
    ):
        """
        Upload vectors to Pinecone

        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs
            metadata: List of metadata dicts
        """
        # Ensure index is initialized
        self.ensure_index()

        # Prepare data in Pinecone format
        data = []
        for i, (vec_id, vector, meta) in enumerate(zip(ids, vectors, metadata)):
            data.append({
                "id": vec_id,
                "values": vector,
                "metadata": meta
            })

        # Batch upsert
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            self.index.upsert(vectors=batch)

        print(f"Uploaded {len(data)} vectors to Pinecone")

    def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            filter_dict: Metadata filters

        Returns:
            List of matches with score and metadata
        """
        # Ensure index is initialized
        self.ensure_index()

        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )

        return [
            {
                "id": match["id"],
                "score": match["score"],
                "metadata": match["metadata"]
            }
            for match in results["matches"]
        ]

    def delete_all(self):
        """Delete all vectors from index"""
        # Ensure index is initialized
        self.ensure_index()

        self.index.delete(delete_all=True)
        print("All vectors deleted from index")

# Export singleton instance
pinecone_client = PineconeClient()