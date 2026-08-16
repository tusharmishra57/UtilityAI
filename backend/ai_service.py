import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not set")

try:
    # Use the requested MiniLM model for embeddings
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Failed to load sentence transformer: {e}")
    embedder = None

def get_embedding(text: str) -> list[float]:
    if not embedder:
        return [0.0] * 384
    # Generate embedding
    embedding = embedder.encode(text)
    return embedding.tolist()

def generate_answer(context: str, question: str) -> str:
    if not GEMINI_API_KEY:
        return "AI is not configured (API key missing)."
        
    prompt = f"""
You are a helpful customer support assistant for an electricity utility platform.
Use the following context (which may include the customer's billing/consumption data and utility policies) to answer the user's question.

Context:
{context}

Question:
{question}

Answer:"""
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        return "I'm sorry, I'm having trouble connecting to my AI backend right now."
