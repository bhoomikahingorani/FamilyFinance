import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import requests

FASTAPI_URL = "http://127.0.0.1:8000/calculate_financial_score"

def calculate_financial_score(row):
    # Weight settings
    savings_income_ratio = row['Savings'] / row['Income'] if row['Income'] > 0 else 0
    expenses_income_ratio = row['MonthlyExpenses'] / row['Income'] if row['Income'] > 0 else 0
    loan_income_ratio = row['LoanPayments'] / row['Income'] if row['Income'] > 0 else 0
    credit_card_spending = row['CreditCardSpending']
    goals_met_percentage = row['FinancialGoalsMet'] / 100

    # Spending category penalty
    travel_entertainment_spending = row['TravelSpending'] + row['EntertainmentSpending']
    category_penalty = travel_entertainment_spending / row['MonthlyExpenses'] if row['MonthlyExpenses'] > 0 else 0

    # csalculation with weights
    score = (
        (savings_income_ratio * 0.3) + 
        (1 - expenses_income_ratio) * 0.2 + 
        (1 - loan_income_ratio) * 0.2 + 
        (1 - credit_card_spending / row['MonthlyExpenses']) * 0.1 + 
        (goals_met_percentage * 0.1) - 
        (category_penalty * 0.1)
    ) * 100

    return max(0, min(100, score))  

def main():
    st.set_page_config(page_title="Financial Insight Dashboard", layout="wide")
    st.title("Financial Insight Dashboard")
    st.sidebar.title("Options")

    uploaded_file = st.sidebar.file_uploader("Upload your financial dataset (CSV)", type=["csv"])
    st.markdown("""
            <style>
                .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                [data-testid="column"] {
                    padding: 0rem 1rem;
                }
            </style>
            """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            family_data = df
            st.write("### Dataset Overview")
            st.dataframe(df.head())

            # Summary statistics
            st.write("### Summary Statistics")
            st.write(df.describe())

            # Spending patterns
            st.write("### Family-level Spending Patterns")
            family_spending = df.groupby('FamilyID')['MonthlyExpenses'].sum().reset_index()
            st.bar_chart(family_spending, x='FamilyID', y='MonthlyExpenses')

            st.write("### Spending Category Distribution")
            category_spending = df.groupby('Category')['Amount'].sum().reset_index()

            # bar chart category-wise
            fig = px.bar(
                category_spending,
                x='Category',
                y='Amount',
                color='Category',  
                title="Total Spending by Category",
                labels={'Amount': 'Total Spending', 'Category': 'Spending Category'},  
                color_discrete_sequence=px.colors.qualitative.Set2  
            )

            st.plotly_chart(fig)

            # Pivot table for spending by category
            pivot_table = pd.pivot_table(
                df,
                values='Amount',  
                index=['FamilyID', 'MemberID'],  
                columns='Category',  
                aggfunc='sum',  
                fill_value=0  
            )

            pivot_table_reset = pivot_table.reset_index()

            st.write("### Pivot Table: Amount Spent by Category")
            st.dataframe(pivot_table_reset)

            # Dropdown for FamilyID 
            family_ids = df['FamilyID'].unique()
            selected_family = st.selectbox("Select a Family ID for Pie Chart", family_ids)

            filtered_data = df[df['FamilyID'] == selected_family]

            category_amounts = filtered_data.groupby('Category')['Amount'].sum().reset_index()

            # CAtegory pie chart
            fig = px.pie(
                category_amounts,
                names='Category',
                values='Amount',
                title=f"Spending Distribution for Family ID: {selected_family}",
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            st.write("### Spending Distribution by Category")
            st.plotly_chart(fig)

            # data for spending category penalty
            data = df[['FamilyID', 'Income', 'Savings', 'MonthlyExpenses', 'LoanPayments', 'CreditCardSpending', 'Dependents', 'FinancialGoalsMet']].drop_duplicates()
            travel_spending = df[df['Category'] == 'Travel'].groupby('FamilyID')['Amount'].sum()
            entertainment_spending = df[df['Category'] == 'Entertainment'].groupby('FamilyID')['Amount'].sum()

            data = data.set_index('FamilyID') 
            data['TravelSpending'] = travel_spending
            data['EntertainmentSpending'] = entertainment_spending
            data[['TravelSpending', 'EntertainmentSpending']] = data[['TravelSpending', 'EntertainmentSpending']].fillna(0)
            data = data.reset_index()

            data['Financial_Score'] = data.apply(calculate_financial_score, axis=1)
            st.dataframe(data)

            # Correlation matrix
            st.write("### Correlation Matrix")
            numeric_data = data.select_dtypes(include=[np.number])
            correlation = numeric_data.corr()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
            st.pyplot(fig)

            # Financial Scoring
            st.write("### Financial Health Scoring")
            st.dataframe(data[['FamilyID', 'Financial_Score']].drop_duplicates())
            st.write(f"Average Financial Score: {data['Financial_Score'].mean():.2f}")

        # Justification for Scoring Logic
            st.write("### Financial Scoring Model Justification")
            st.markdown("""
            The financial scoring model evaluates an individual's financial health by incorporating several key factors, each assigned a specific weight based on its importance. Below is the rationale behind the scoring logic:

            1. **Savings-to-Income Ratio (30%)**: A high ratio indicates strong financial stability and preparedness for emergencies.
            2. **Expenses-to-Income Ratio (20%)**: Controlled expenses relative to income demonstrate better financial management.
            3. **Loan Payments-to-Income Ratio (20%)**: A lower ratio reflects fewer financial obligations and greater flexibility.
            4. **Credit Card Spending-to-Expenses Ratio (10%)**: A lower ratio indicates disciplined short-term financial habits.
            5. **Financial Goals Met (10%)**: Measures progress toward long-term objectives, reflecting planning and discipline.
            6. **Discretionary Spending Penalty (-10%)**: High spending on travel and entertainment can impact savings and stability.

            The scoring model ensures that savings and responsible spending are prioritized, while excessive discretionary spending is discouraged. The final score, capped between 0 and 100, provides a comprehensive assessment of financial health.
            """)

    with col2:
        st.write("### Add a New Family Record")
        FamilyID = st.number_input("Family ID", min_value=201)
        Income = st.number_input("Income", min_value=0.0)
        Savings = st.number_input("Savings", min_value=0.0)
        MonthlyExpenses = st.number_input("Monthly Expenses", min_value=0.0)
        LoanPayments = st.number_input("Loan Payments", min_value=0.0)
        CreditCardSpending = st.number_input("Credit Card Spending", min_value=0.0)
        TravelSpending = st.number_input("Travel Spending", min_value=0.0)
        EntertainmentSpending = st.number_input("Entertainment Spending", min_value=0.0)
        Dependents = st.number_input("Dependents", min_value=0)
        FinancialGoalsMet = st.number_input("Financial Goals Met", min_value=0, max_value=100)

        if st.button("Calculate Score for New Family"):
            new_family_data = {
                "FamilyID": FamilyID,
                "Income": Income,
                "Savings": Savings,
                "MonthlyExpenses": MonthlyExpenses,
                "LoanPayments": LoanPayments,
                "CreditCardSpending": CreditCardSpending,
                "TravelSpending": TravelSpending,
                "EntertainmentSpending": EntertainmentSpending,
                "Dependents": Dependents,
                "FinancialGoalsMet": FinancialGoalsMet
            }

            new_family_df = pd.DataFrame([new_family_data])
            new_family_df['Financial_Score'] = new_family_df.apply(calculate_financial_score, axis=1)
            data = pd.concat([data, new_family_df], ignore_index=True)
    
            try:
                response = requests.post(FASTAPI_URL, json=new_family_data)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Financial Score: {result['FinancialScore']}")
                    st.info(f"Insights: {result['Insights']}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}") 

            # Download updated dataset
            st.write("### Download Scored Dataset")
            scored_csv = data.to_csv(index=False).encode('utf-8')
            st.download_button("Download Scored CSV", data=scored_csv, file_name="scored_financial_data.csv", mime="text/csv")

if __name__ == "__main__":
    main()
