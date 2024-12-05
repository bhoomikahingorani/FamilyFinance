# Financial Insight Dashboard

This project is a web application that provides financial insights and scoring based on user-uploaded financial data. It consists of a Streamlit frontend (`streamlit_app.py`) and a FastAPI backend (`fastAPI.py`).

## Financial Scoring Model

### Score Components and Weights

The financial health score (0-100) is calculated using the following components:

1. **Savings-to-Income Ratio (30%)**
   - Measures financial security and emergency preparedness
   - Higher ratio = better score
   - Formula: `(Savings / Income) * 0.3`

2. **Expenses-to-Income Ratio (20%)**
   - Evaluates spending discipline
   - Lower ratio = better score
   - Formula: `(1 - MonthlyExpenses / Income) * 0.2`

3. **Loan Burden Ratio (20%)**
   - Assesses debt management
   - Lower ratio = better score
   - Formula: `(1 - LoanPayments / Income) * 0.2`

4. **Credit Card Usage (10%)**
   - Measures short-term financial behavior
   - Lower ratio = better score
   - Formula: `(1 - CreditCardSpending / MonthlyExpenses) * 0.1`

5. **Financial Goals Achievement (10%)**
   - Tracks progress towards financial objectives
   - Higher percentage = better score
   - Formula: `(FinancialGoalsMet / 100) * 0.1`

6. **Discretionary Spending Penalty (-10%)**
   - Penalizes excessive non-essential spending
   - Higher spending = larger penalty
   - Formula: `((TravelSpending + EntertainmentSpending) / MonthlyExpenses) * 0.1`

## Features

- Upload financial datasets in CSV format.
- Visualize spending patterns and category distributions.
- Calculate and display financial scores for families.
- Download updated datasets with financial scores.
- Add new family records and calculate their financial scores using the FastAPI backend.

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bhoomikahingorani/FamilyFinance.git
   cd financial-insight-dashboard
   ```

2. Install the required packages:

   ```bash
   pip install pandas seaborn matplotlib plotly
   pip install streamlit requests
   pip install fastapi uvicorn

   ```

3. Start the FastAPI server:

   ```bash
   uvicorn fastAPI:app --reload
   ```

4. Run the Streamlit app:

   ```bash
   streamlit run streamlit_app.py
   ```
## API Endpoints

### POST /calculate_financial_score
Calculates financial score for a single family record

Request body:
```json
{
    "FamilyID": int,
    "Income": float,
    "Savings": float,
    "MonthlyExpenses": float,
    "LoanPayments": float,
    "CreditCardSpending": float,
    "TravelSpending": float,
    "EntertainmentSpending": float,
    "FinancialGoalsMet": int
}
```

Response:
```json
{
    "FamilyID": int,
    "FinancialScore": float,
    "Insights": string
}
```

## Usage

1. Open the Streamlit app in your browser.
2. Upload 'family_financial_and_transactions_data' dataset in CSV format.
3. Explore the visualizations and insights provided by the dashboard.
4. Add new family records and calculate their financial scores.
5. Download the updated dataset with financial scores.

## File Descriptions

- **streamlit_app.py**: The main Streamlit application file. It handles the user interface, data visualization, and interaction with the FastAPI backend.
- **fastAPI.py**: The FastAPI backend that calculates financial scores for new family records.
	
