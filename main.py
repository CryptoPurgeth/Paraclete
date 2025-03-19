from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import pdfkit

# Load environment variables
load_dotenv()

app = FastAPI()

# Ensure OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Please check your .env file.")

openai.api_key = OPENAI_API_KEY

# Request model for AI chat
class UserInput(BaseModel):
    session_id: str
    question: str

# Request model for financial plan
class FinancialPlanRequest(BaseModel):
    session_id: str
    name: str
    age: int
    marital_status: str
    income: float
    investment_preference: str
    retirement_age: int

@app.get("/")
async def root():
    return {"message": "Welcome to Paraclete AI"}

@app.post("/ask")
async def get_financial_advice(user_input: UserInput):
    """Handles AI financial advice chat interaction."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input.question}],
            max_tokens=200
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_plan")
async def generate_financial_plan(data: FinancialPlanRequest):
    """Generates a PDF financial plan based on user input."""
    try:
        pdf_content = f"""
        <h1>Personalized Financial Plan</h1>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Age:</strong> {data.age}</p>
        <p><strong>Marital Status:</strong> {data.marital_status}</p>
        <p><strong>Income:</strong> ${data.income}</p>
        <p><strong>Investment Preference:</strong> {data.investment_preference}</p>
        <p><strong>Retirement Age:</strong> {data.retirement_age}</p>
        <h2>AI Recommendations:</h2>
        """

        # Generate AI advice for plan
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Create a detailed financial plan for someone who is {data.age} years old, earns {data.income}, prefers {data.investment_preference} investments, and wants to retire at {data.retirement_age}."}
            ],
            max_tokens=500
        )
        pdf_content += f"<p>{response.choices[0].message.content}</p>"

        # Save PDF
        pdf_filename = f"{data.session_id}_financial_plan.pdf"
        pdfkit.from_string(pdf_content, pdf_filename)

        return FileResponse(pdf_filename, filename="financial_plan.pdf", media_type="application/pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

























