import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Loan Calculator",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Loan Repayment Calculator")
st.caption("Simple, mobile-friendly demo app built with Streamlit")

# ---------- Inputs ----------
st.subheader("Loan details")

loan_amount = st.number_input(
    "Loan amount",
    min_value=1000.0,
    value=100000.0,
    step=1000.0,
    format="%.2f"
)

annual_rate = st.number_input(
    "Annual interest rate (%)",
    min_value=0.0,
    value=5.0,
    step=0.1,
    format="%.2f"
)

years = st.number_input(
    "Loan term (years)",
    min_value=1,
    value=20,
    step=1
)

show_schedule = st.toggle("Show amortization schedule", value=False)

# ---------- Calculations ----------
months = int(years * 12)
monthly_rate = annual_rate / 100 / 12

if monthly_rate == 0:
    monthly_payment = loan_amount / months
else:
    monthly_payment = loan_amount * (
        monthly_rate * (1 + monthly_rate) ** months
    ) / ((1 + monthly_rate) ** months - 1)

total_payment = monthly_payment * months
total_interest = total_payment - loan_amount

# ---------- Summary ----------
st.subheader("Results")

col1, col2, col3 = st.columns(3)
col1.metric("Monthly payment", f"${monthly_payment:,.2f}")
col2.metric("Total payment", f"${total_payment:,.2f}")
col3.metric("Total interest", f"${total_interest:,.2f}")

# ---------- Amortization ----------
balance = loan_amount
schedule = []

for month in range(1, months + 1):
    interest_payment = balance * monthly_rate if monthly_rate > 0 else 0
    principal_payment = monthly_payment - interest_payment

    # protect final row from tiny floating issues
    if principal_payment > balance:
        principal_payment = balance

    balance -= principal_payment
    if balance < 0:
        balance = 0

    schedule.append(
        {
            "Month": month,
            "Payment": round(monthly_payment, 2),
            "Principal": round(principal_payment, 2),
            "Interest": round(interest_payment, 2),
            "Balance": round(balance, 2),
        }
    )

df = pd.DataFrame(schedule)

# ---------- Charts ----------
st.subheader("Balance over time")
st.line_chart(df.set_index("Month")["Balance"], use_container_width=True)

st.subheader("Principal vs interest")
st.line_chart(
    df.set_index("Month")[["Principal", "Interest"]],
    use_container_width=True
)

# ---------- Optional table ----------
if show_schedule:
    st.subheader("Amortization schedule")
    st.dataframe(df, use_container_width=True, hide_index=True)
