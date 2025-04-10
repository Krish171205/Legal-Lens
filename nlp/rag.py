import subprocess
import pinecone
from sentence_transformers import SentenceTransformer

# SentenceTransformer model for embeddings
EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

class RAG:
    def __init__(
        self,
        index_name: str,
        pinecone_api_key: str,
        pinecone_env: str
    ):
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(index_name)

    def index_document(self, doc_id: str, text: str):
        emb = EMBED_MODEL.encode(text).tolist()
        self.index.upsert([(doc_id, emb, {"text": text})])

    def query(self, query_text: str, top_k: int = 5):
        q_emb = EMBED_MODEL.encode(query_text).tolist()
        res = self.index.query(q_emb, top_k=top_k, include_metadata=True)
        return [match['metadata']['text'] for match in res['matches']]

    def generate_answer(self, question: str, context_texts: list) -> str:
        context = "\n\n".join(context_texts)
        prompt = (
            f"Use the following context to answer the legal question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\nAnswer:"
        )
        result = subprocess.run(
            ["ollama", "run", "mistral", "-p", prompt],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()