from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import pdfkit
import os
from dotenv import load_dotenv

# Load environment variables (OpenAI key, etc.)
load_dotenv()

app = FastAPI()

# ----------------- CORS Middleware -----------------
# Allow requests from any origin (Wix front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://your-wix-domain.com"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- OpenAI Setup -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key not found. Check your .env file or environment variables.")
openai.api_key = OPENAI_API_KEY

# ----------------- Models -----------------
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

# ----------------- /ask Endpoint (AI Chat) -----------------
@app.post("/ask")
def get_financial_advice(user_input: UserInput):
    """
    Receives a question from Wix, sends it to OpenAI, and returns an AI response.
    Expects JSON: { "session_id": "...", "question": "..." }
    Returns JSON: { "response": "AI answer" }
    """
    try:
        # Create chat completion with GPT-4 or gpt-3.5-turbo
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if your plan doesn't have GPT-4
            messages=[{"role": "user", "content": user_input.question}],
            max_tokens=150
        )
        ai_text = response.choices[0].message.content
        return {"response": ai_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- /generate_plan Endpoint (PDF) -----------------
@app.post("/generate_plan")
def generate_plan(data: FinancialPlanRequest):
    """
    Generates a financial plan PDF based on user input and returns it.
    Expects JSON with fields:
      session_id, name, age, marital_status, income, investment_preference, retirement_age
    Returns a downloadable PDF file.
    """
    try:
        # Create a simple HTML plan
        plan_html = f"""
        <h1>Financial Plan for {data.name}</h1>
        <p><strong>Age:</strong> {data.age}</p>
        <p><strong>Marital Status:</strong> {data.marital_status}</p>
        <p><strong>Annual Income:</strong> ${data.income:,.2f}</p>
        <p><strong>Investment Preference:</strong> {data.investment_preference}</p>
        <p><strong>Planned Retirement Age:</strong> {data.retirement_age}</p>
        <hr>
        <p>This basic plan outlines some initial steps. For a more detailed strategy,
           consider scheduling a consultation with a licensed advisor.</p>
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


























