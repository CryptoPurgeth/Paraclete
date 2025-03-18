from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from fpdf import FPDF
from fastapi.responses import FileResponse
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define input model
class UserInput(BaseModel):
    session_id: str
    question: str

class FinancialInfo(BaseModel):
    name: str
    age: int
    marital_status: str
    income: int
    investment_preference: str
    retirement_age: int

@app.get("/")
def read_root():
    return {"message": "Welcome to the Paraclete AI API"}

@app.post("/ask")
def get_financial_advice(user_input: UserInput):
    try:
        response = openai.ChatCompletion.create(  # ✅ Fixed method
            model="gpt-4",
            messages=[{"role": "user", "content": user_input.question}]
        )
        return {"response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_plan")
def generate_plan(financial_data: FinancialInfo):
    try:
        summary = f"""
        Financial Plan for {financial_data.name}
        -----------------------------------------
        - Age: {financial_data.age}
        - Marital Status: {financial_data.marital_status}
        - Income: ${financial_data.income}
        - Investment Preference: {financial_data.investment_preference}
        - Retirement Age: {financial_data.retirement_age}

        Recommended Strategy:
        - Diversified investment portfolio including stocks, bonds, and ETFs.
        - Maintain an emergency fund covering 6 months of expenses.
        - Maximize tax-advantaged retirement contributions.
        - Consider passive income options like REITs or dividend stocks.
        """

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, summary)

        pdf_path = "financial_plan.pdf"
        pdf.output(pdf_path)

        return FileResponse(pdf_path, media_type="application/pdf", filename="financial_plan.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))























