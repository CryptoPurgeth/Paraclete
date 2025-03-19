from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import pdfkit
import os
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

app = FastAPI()

# -----------------------------
# CORS Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For stricter security, replace "*" with your Wix domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# OpenAI Setup
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Check your .env or environment variables.")
openai.api_key = OPENAI_API_KEY

# -----------------------------
# Data Models
# -----------------------------
class UserInput(BaseModel):
    session_id: str
    question: str

class FinancialPlanRequest(BaseModel):
    session_id: str
    name: str
    age: int
    marital_status: str
    income: float
    investment_preference: str
    retirement_age: int

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to Paraclete AI"}

# -----------------------------
# /ask endpoint
# -----------------------------
@app.post("/ask")
def get_financial_advice(user_input: UserInput):
    """
    Receives a question (from Wix chat), sends it to GPT, returns short AI response.
    Expects JSON: { "session_id": "...", "question": "..." }
    Returns: { "response": "..." }
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": user_input.question}],
            max_tokens=150
        )
        ai_text = response.choices[0].message.content.strip()
        return {"response": ai_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# /generate_plan endpoint
# -----------------------------
@app.post("/generate_plan")
def generate_plan(data: FinancialPlanRequest):
    """
    Generates a detailed, personalized financial plan (PDF) using GPT's recommendations.
    Expects JSON: {
      "session_id": "...",
      "name": "...",
      "age": ...,
      "marital_status": "...",
      "income": ...,
      "investment_preference": "...",
      "retirement_age": ...
    }
    Returns: A downloadable PDF file.
    """
    try:
        # Build a robust prompt for GPT
        ai_prompt = (
            f"Please create a thorough, step-by-step financial roadmap for {data.name}, "
            f"age {data.age}, {data.marital_status}, "
            f"who earns ${data.income:,.2f} annually, prefers {data.investment_preference} investments, "
            f"and plans to retire at {data.retirement_age}. "
            "Include budgeting, saving, investing, and retirement strategies. "
            "Approximate monthly contributions if possible, highlight potential pitfalls, "
            "and outline realistic steps to achieve these goals."
        )

        # GPT call
        ai_response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=1000,    # Enough tokens for a detailed response
            temperature=0.7     # Adjust if you want more or less creativity
        )
        recommendations = ai_response.choices[0].message.content.strip()

        # Combine user data + GPT text into HTML
        plan_html = f"""
        <h1 style="text-align:center;">Detailed Financial Plan for {data.name}</h1>
        <p><strong>Age:</strong> {data.age}</p>
        <p><strong>Marital Status:</strong> {data.marital_status}</p>
        <p><strong>Annual Income:</strong> ${data.income:,.2f}</p>
        <p><strong>Investment Preference:</strong> {data.investment_preference}</p>
        <p><strong>Planned Retirement Age:</strong> {data.retirement_age}</p>
        <hr>
        <h2 style="color:#444;">AI Roadmap & Recommendations</h2>
        <p>{recommendations}</p>
        <hr>
        <p style="font-style:italic;">
          Disclaimer: This plan is informational. For personal advice, consult a licensed professional.
        </p>
        """

        # Convert HTML to PDF
        pdf_filename = f"{data.session_id}_financial_plan.pdf"
        pdfkit.from_string(plan_html, pdf_filename)

        # Return the PDF file
        return FileResponse(
            pdf_filename,
            media_type="application/pdf",
            filename="financial_plan.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




























