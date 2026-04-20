import streamlit as st
import pandas as pd
import altair as alt

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
    value=5,
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

    if principal_payment > balance:
        principal_payment = balance

    balance -= principal_payment
    if balance < 0:
        balance = 0

    year_number = ((month - 1) // 12) + 1
    month_in_year = ((month - 1) % 12) + 1
    period_label = f"Y{year_number}-M{month_in_year}"

    schedule.append(
        {
            "Month": month,
            "Year": year_number,
            "Month in Year": month_in_year,
            "Period": period_label,
            "Payment": round(monthly_payment, 2),
            "Principal": round(principal_payment, 2),
            "Interest": round(interest_payment, 2),
            "Balance": round(balance, 2),
        }
    )

df = pd.DataFrame(schedule)

# ---------- Balance chart ----------
st.subheader("Balance over time")
balance_chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X(
        "Period:N",
        sort=None,
        axis=alt.Axis(title="Time", labelAngle=-45)
    ),
    y=alt.Y("Balance:Q", title="Remaining balance"),
    tooltip=["Period", "Balance"]
).properties(height=350)

st.altair_chart(balance_chart, use_container_width=True)

# ---------- Principal vs Interest stacked bar ----------
st.subheader("Payment breakdown")

chart_df = df[["Period", "Principal", "Interest"]].melt(
    id_vars="Period",
    value_vars=["Principal", "Interest"],
    var_name="Type",
    value_name="Amount"
)

bar_chart = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X(
        "Period:N",
        sort=None,
        axis=alt.Axis(title="Time (Year-Month)", labelAngle=-45)
    ),
    y=alt.Y("Amount:Q", title="Payment amount", stack="zero"),
    color=alt.Color(
        "Type:N",
        scale=alt.Scale(
            domain=["Principal", "Interest"],
            range=["#4F81BD", "#C0504D"]
        )
    ),
    tooltip=["Period", "Type", "Amount"]
).properties(height=350)

st.altair_chart(bar_chart, use_container_width=True)

# ---------- Yearly summary ----------
st.subheader("Yearly view")

yearly_df = df.groupby("Year", as_index=False).agg({
    "Principal": "sum",
    "Interest": "sum",
    "Balance": "last"
})

yearly_chart_df = yearly_df.melt(
    id_vars="Year",
    value_vars=["Principal", "Interest"],
    var_name="Type",
    value_name="Amount"
)

yearly_bar_chart = alt.Chart(yearly_chart_df).mark_bar().encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Amount:Q", title="Total paid in year", stack="zero"),
    color=alt.Color(
        "Type:N",
        scale=alt.Scale(
            domain=["Principal", "Interest"],
            range=["#4F81BD", "#C0504D"]
        )
    ),
    tooltip=["Year", "Type", "Amount"]
).properties(height=350)

st.altair_chart(yearly_bar_chart, use_container_width=True)

# ---------- Optional schedule ----------
if show_schedule:
    st.subheader("Amortization schedule")
    st.dataframe(df, use_container_width=True, hide_index=True)
