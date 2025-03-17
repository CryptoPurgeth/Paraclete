from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from fpdf import FPDF
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request model for chat
class UserInput(BaseModel):
    session_id: str
    question: str

# Request model for financial plan generation
class FinancialInfo(BaseModel):
    name: str
    age: int
    marital_status: str
    income: float
    investment_preference: str
    retirement_age: int

@app.post("/ask")
async def get_financial_advice(user_input: UserInput):
    """Handles user questions and returns AI-generated financial advice"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input.question}]
        )
        
        answer = response["choices"][0]["message"]["content"]
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

@app.post("/generate_plan")
async def generate_plan(financial_data: FinancialInfo):
    """Generates a financial plan PDF based on user input"""
    try:
        # Create the financial plan text using OpenAI
        prompt = f"""
        Generate a comprehensive financial plan for {financial_data.name}, who is {financial_data.age} years old,
        {financial_data.marital_status}, earning ${financial_data.income} annually, with an investment preference
        of {financial_data.investment_preference}. Their target retirement age is {financial_data.retirement_age}.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        plan_text = response["choices"][0]["message"]["content"]
        
        # Generate PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style='', size=12)
        pdf.multi_cell(0, 10, plan_text)

        # Save PDF file
        filename = f"financial_plan_{uuid.uuid4().hex}.pdf"
        filepath = f"/tmp/{filename}"
        pdf.output(filepath)

        return FileResponse(filepath, media_type="application/pdf", filename="Financial_Plan.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to Paraclete Financial AI"}

@app.get("/health")
def health_check():
    return {"status": "ok"}













