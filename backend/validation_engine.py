from langchain_huggingface import HuggingFaceEmbeddings
import os
import faiss
import numpy as np
import pickle
from dotenv import load_dotenv

load_dotenv()

class ValidationEngine:
    def __init__(self, api_key: str = None, persist_directory: str = "./knowledge_base/faiss_index"):
        self.persist_directory = persist_directory
        self.index_path = os.path.join(persist_directory, "index.faiss")
        self.meta_path = os.path.join(persist_directory, "metadata.pkl")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def get_embedding(self, text: str):
        # Local embedding generation
        embedding = self.embeddings.embed_query(text)
        return np.array(embedding).astype('float32').reshape(1, -1)

    def add_reference_doc(self, doc_id: str, content: str, metadata: dict):
        embedding = self.get_embedding(content)
        self.index.add(embedding)
        self.metadata.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata
        })
        self.save_index()

    def validate_content(self, generated_content: str, n_results: int = 2) -> list:
        if self.index.ntotal == 0:
            return []
            
        embedding = self.get_embedding(generated_content)
        distances, indices = self.index.search(embedding, n_results)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx]["content"])
        return results

    def add_feedback(self, scope_json: str, framework_json: str, feedback_text: str):
        import time
        doc_id = f"feedback-{int(time.time())}"
        content = (
            "SCOPE\n" + scope_json + "\n\n" +
            "FRAMEWORK\n" + framework_json + "\n\n" +
            "FEEDBACK\n" + feedback_text
        )
        self.add_reference_doc(
            doc_id=doc_id,
            content=content,
            metadata={"type": "feedback"}
        )

    def find_best_match(self, text: str):
        if self.index.ntotal == 0:
            return None
        embedding = self.get_embedding(text)
        distances, indices = self.index.search(embedding, 1)
        idx = int(indices[0][0])
        if idx == -1 or idx >= len(self.metadata):
            return None
        return {
            "distance": float(distances[0][0]),
            "content": self.metadata[idx]["content"],
            "id": self.metadata[idx]["id"],
        }

    def parse_expected_output(self, kb_content: str) -> str:
        parts = kb_content.split("EXPECTED_OUTPUT:\n", 1)
        if len(parts) == 2:
            return parts[1]
        return kb_content

    def find_best_expected_output(self, text: str) -> str | None:
        best = self.find_best_match(text)
        if not best:
            return None
        return self.parse_expected_output(best["content"])

