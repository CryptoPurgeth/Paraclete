import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

# Load environment variables
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any frontend (change to specific domain for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define request model
class UserInput(BaseModel):
    session_id: str  # Unique session identifier
    question: str

@app.get("/")
def read_root():
    """Welcome message for API root"""
    return {"message": "Welcome to Paraclete AI - Your Trusted Financial Guide!"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "running"}

@app.post("/ask")
def get_financial_advice(input_data: UserInput):
    """Handles user questions, stores conversation in Supabase, and returns AI-generated financial advice"""
    session_id = input_data.session_id
    user_question = input_data.question

    try:
        # Check if session exists in the database
        response = supabase.table("user_sessions").select("*").eq("session_id", session_id).execute()
        data = response.data

        if not data:  # If session does not exist, create it
            chat_history = [{"role": "system", "content": "You are an expert financial advisor."}]
            supabase.table("user_sessions").insert({"session_id": session_id, "messages": chat_history}).execute()
        else:
            chat_history = data[0]["messages"]

        # Add user question to session history
        chat_history.append({"role": "user", "content": user_question})

        # Generate AI response
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_history
        )
        ai_response = response.choices[0].message.content

        # Add AI response to session history
        chat_history.append({"role": "assistant", "content": ai_response})

        # Update session in Supabase
        supabase.table("user_sessions").update({"messages": chat_history}).eq("session_id", session_id).execute()

        return {"response": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define port for Render (Dynamic)
port = int(os.getenv("PORT", 8000))  # Uses Render-assigned port or defaults to 8000 locally

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)




