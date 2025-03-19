from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import pdfkit
import os
from dotenv import load_dotenv

# ----------------- Load environment variables -----------------
load_dotenv()

# ----------------- Create FastAPI app -----------------
app = FastAPI()

# ----------------- CORS Middleware (to allow Wix) -----------------
# For security, replace "*" with your Wix domain if you want to restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- OpenAI Setup -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key not found. Check your .env or environment variables.")
openai.api_key = OPENAI_API_KEY

# ----------------- Data Models -----------------
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

# ----------------- Root Endpoint -----------------
@app.get("/")
def read_root():
    return {"message": "Welcome to Paraclete AI"}

# ----------------- /ask Endpoint -----------------
@app.post("/ask")
def get_financial_advice(user_input: UserInput):
    """
    Receives a user question, calls OpenAI for a short chat response, returns { "response": "..." }
    """
    try:
        # Example using GPT-4. If not available, switch to "gpt-3.5-turbo".
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input.question}],
            max_tokens=150
        )
        ai_text = response.choices[0].message.content
        return {"response": ai_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- /generate_plan Endpoint -----------------
@app.post("/generate_plan")
def generate_plan(data: FinancialPlanRequest):
    """
    Generates a detailed financial plan with AI recommendations, returns a PDF file.
    """
    try:
        # 1) Build a prompt with user info
        ai_prompt = (
            f"Create a detailed financial plan for {data.name}, "
            f"who is {data.age} years old, {data.marital_status}, "
            f"with an annual income of {data.income}, preferring {data.investment_preference} investments, "
            f"and planning to retire at {data.retirement_age}. "
            "Provide step-by-step savings, investing, and retirement strategies."
        )

        # 2) Get AI recommendations from OpenAI
        ai_response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": ai_prompt}],
            max_tokens=500
        )
        recommendations = ai_response.choices[0].message.content

        # 3) Combine user info + AI text into an HTML string
        plan_html = f"""
        <h1 style="text-align:center;">Financial Plan for {data.name}</h1>
        <p><strong>Age:</strong> {data.age}</p>
        <p><strong>Marital Status:</strong> {data.marital_status}</p>
        <p><strong>Annual Income:</strong> ${data.income:,.2f}</p>
        <p><strong>Investment Preference:</strong> {data.investment_preference}</p>
        <p><strong>Retirement Age:</strong> {data.retirement_age}</p>
        <hr>
        <h2 style="color:#444;">AI Recommendations</h2>
        <p>{recommendations}</p>
        <hr>
        <p><em>This plan is for informational purposes. For personalized advice, consult a licensed financial advisor.</em></p>
        """

        # 4) Convert HTML to PDF using pdfkit
        pdf_filename = f"{data.session_id}_financial_plan.pdf"
        pdfkit.from_string(plan_html, pdf_filename)

        # 5) Return the generated PDF
        return FileResponse(
            pdf_filename,
            media_type="application/pdf",
            filename="financial_plan.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



























