from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from streamlit_app import calculate_financial_score

app = FastAPI()

class FinancialData(BaseModel):
    FamilyID: int
    Income: float
    Savings: float
    MonthlyExpenses: float
    LoanPayments: float
    CreditCardSpending: float
    TravelSpending: float
    EntertainmentSpending: float
    FinancialGoalsMet: int

class FinancialScoreResponse(BaseModel):
    FamilyID: int
    FinancialScore: float
    Insights: str

@app.post("/calculate_financial_score", response_model=FinancialScoreResponse)
def calculate_score(data: FinancialData):
    try:
        
        row = data.dict()
        score = calculate_financial_score(row)
        
        insights = []
        if row['Savings'] / row['Income'] < 0.2:
            insights.append("Savings are below recommended levels, affecting your score.")
        if row['MonthlyExpenses'] / row['Income'] > 0.6:
            insights.append("High expenses reduce your financial flexibility.")
        if row['LoanPayments'] / row['Income'] > 0.3:
            insights.append("Loan payments exceed a healthy ratio.")
        
        insights = " ".join(insights) if insights else "Your financial profile is balanced."

        return FinancialScoreResponse(FamilyID=row['FamilyID'], FinancialScore=score, Insights=insights)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))