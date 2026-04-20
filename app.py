import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Loan Repayment Calculator", layout="wide")

st.title("Loan Repayment Calculator")
st.write("Enter the loan details to calculate the monthly payment and see the repayment breakdown.")

# Inputs
st.sidebar.header("Loan Inputs")

loan_amount = st.sidebar.number_input("Loan Amount", min_value=1000.0, value=100000.0, step=1000.0)
annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)
years = st.sidebar.number_input("Loan Term (Years)", min_value=1, value=20, step=1)

# Calculations
months = years * 12
monthly_rate = annual_rate / 100 / 12

if monthly_rate == 0:
    monthly_payment = loan_amount / months
else:
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

total_payment = monthly_payment * months
total_interest = total_payment - loan_amount

# Top results
col1, col2, col3 = st.columns(3)

col1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
col2.metric("Total Payment", f"${total_payment:,.2f}")
col3.metric("Total Interest", f"${total_interest:,.2f}")

# Amortization table
balance = loan_amount
schedule = []

for month in range(1, months + 1):
    interest_payment = balance * monthly_rate
    principal_payment = monthly_payment - interest_payment
    if monthly_rate == 0:
        interest_payment = 0
        principal_payment = monthly_payment

    balance -= principal_payment
    if balance < 0:
        balance = 0

    schedule.append({
        "Month": month,
        "Payment": monthly_payment,
        "Principal": principal_payment,
        "Interest": interest_payment,
        "Balance": balance
    })

df = pd.DataFrame(schedule)

st.subheader("Amortization Schedule")
st.dataframe(
    df.style.format({
        "Payment": "${:,.2f}",
        "Principal": "${:,.2f}",
        "Interest": "${:,.2f}",
        "Balance": "${:,.2f}"
    }),
    use_container_width=True
)

# Chart
st.subheader("Loan Balance Over Time")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Month"], df["Balance"])
ax.set_xlabel("Month")
ax.set_ylabel("Remaining Balance")
ax.set_title("Remaining Loan Balance")
st.pyplot(fig)

# Principal vs interest chart
st.subheader("Principal vs Interest Payments")

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(df["Month"], df["Principal"], label="Principal")
ax2.plot(df["Month"], df["Interest"], label="Interest")
ax2.set_xlabel("Month")
ax2.set_ylabel("Amount")
ax2.set_title("Monthly Payment Breakdown")
ax2.legend()
st.pyplot(fig2)
