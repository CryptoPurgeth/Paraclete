from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fpdf import FPDF
import os

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware (Fixes 403 Forbidden Issues)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class FinancialInfo(BaseModel):
    name: str
    age: int
    marital_status: str
    income: float
    investment_preference: str
    retirement_age: int

# Function to generate financial plan PDF
def generate_pdf(data: FinancialInfo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Personalized Financial Plan", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Name: {data.name}", ln=True)
    pdf.cell(200, 10, f"Age: {data.age}", ln=True)
    pdf.cell(200, 10, f"Marital Status: {data.marital_status}", ln=True)
    pdf.cell(200, 10, f"Annual Income: ${data.income:,.2f}", ln=True)
    pdf.cell(200, 10, f"Investment Strategy: {data.investment_preference}", ln=True)
    pdf.cell(200, 10, f"Planned Retirement Age: {data.retirement_age}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Investment Strategy Recommendations:", ln=True, align="L")

    if data.investment_preference == "Conservative":
        pdf.cell(200, 10, "- Focus on Bonds, CDs, and Dividend Stocks", ln=True)
    elif data.investment_preference == "Balanced":
        pdf.cell(200, 10, "- Mix of Stocks, Bonds, and ETFs", ln=True)
    elif data.investment_preference == "Aggressive":
        pdf.cell(200, 10, "- Higher exposure to Stocks and Crypto", ln=True)

    file_name = f"{data.name.replace(' ', '_')}_Financial_Plan.pdf"
    pdf_path = f"/tmp/{file_name}"  # Render allows file writing in /tmp/
    pdf.output(pdf_path)
    return file_name, pdf_path

# API Endpoint to generate the financial plan
@app.post("/generate_plan")
def generate_plan(financial_data: FinancialInfo):
    try:
        file_name, pdf_path = generate_pdf(financial_data)
        return {"pdf_url": f"https://paraclete.onrender.com/download/{file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Endpoint to serve PDF files
@app.get("/download/{pdf_name}")
def download_pdf(pdf_name: str):
    file_path = f"/tmp/{pdf_name}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=pdf_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Start the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)










