from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Finance Laboratory",
    page_icon="🧪",
    layout="centered"
)

# -----------------------------
# Helpers
# -----------------------------
def currency_fmt(x):
    return f"${x:,.2f}"

def find_calculator_image():
    possible_files = [
        "Calculator.png",
        "Calculator.jpg",
        "Calculator.jpeg",
        "Calculator.webp",
    ]
    for file_name in possible_files:
        if Path(file_name).exists():
            return file_name
    return None

def build_schedule(loan_amount, annual_rate, years):
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
                "MonthInYear": month_in_year,
                "Period": period_label,
                "Payment": round(monthly_payment, 2),
                "Principal": round(principal_payment, 2),
                "Interest": round(interest_payment, 2),
                "Balance": round(balance, 2),
            }
        )

    df = pd.DataFrame(schedule)

    yearly_df = (
        df.groupby("Year", as_index=False)
        .agg(
            Principal=("Principal", "sum"),
            Interest=("Interest", "sum"),
            Balance=("Balance", "last"),
        )
    )

    yearly_df["YearLabel"] = yearly_df["Year"].apply(lambda y: f"Y{y}")

    return df, yearly_df, monthly_payment, total_payment, total_interest

def go_to(page_name):
    st.session_state.page = page_name

# -----------------------------
# Session state
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -----------------------------
# Home page
# -----------------------------
if st.session_state.page == "home":
    st.title("🧪 Welcome to Finance Laboratory")
    st.subheader("Explore our interactive financial tools")

    image_path = find_calculator_image()
    if image_path:
        st.image(image_path, use_container_width=True)

    st.write(
        "This page showcases interactive financial calculators and simulators. "
        "Each tool is designed to make finance easier to understand through visual, practical examples."
    )

    st.markdown("### Available tools")
    st.button("Loan Calculator", use_container_width=True, on_click=go_to, args=("loan",))

# -----------------------------
# Loan calculator page
# -----------------------------
elif st.session_state.page == "loan":
    top_left, top_right = st.columns([1, 4])

    with top_left:
        st.button("← Back", on_click=go_to, args=("home",), use_container_width=True)

    with top_right:
        st.title("💰 Loan Repayment Calculator")

    st.caption("Simple, mobile-friendly demo")

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

    df, yearly_df, monthly_payment, total_payment, total_interest = build_schedule(
        loan_amount, annual_rate, years
    )

    st.subheader("Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly payment", currency_fmt(monthly_payment))
    col2.metric("Total payment", currency_fmt(total_payment))
    col3.metric("Total interest", currency_fmt(total_interest))

    # Common year markers for monthly charts
    year_marker_months = [(year - 1) * 12 + 1 for year in yearly_df["Year"].tolist()]

    # -----------------------------
    # Chart 1: Balance over time
    # -----------------------------
    st.subheader("Balance over time")

    balance_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "Month:Q",
                title="Time",
                scale=alt.Scale(domain=[1, len(df)]),
                axis=alt.Axis(
                    values=year_marker_months,
                    labelExpr="'Y' + floor((datum.value - 1)/12 + 1)",
                    labelAngle=0,
                    grid=False
                )
            ),
            y=alt.Y("Balance:Q", title="Remaining balance"),
            tooltip=[
                alt.Tooltip("Period:N", title="Period"),
                alt.Tooltip("Balance:Q", title="Balance", format=",.2f")
            ]
        )
        .properties(height=320)
    )

    st.altair_chart(balance_chart, use_container_width=True)

    # -----------------------------
    # Chart 2: Payment breakdown
    # -----------------------------
    st.subheader("Payment breakdown")

    monthly_chart_df = df[["Month", "Period", "Principal", "Interest"]].melt(
        id_vars=["Month", "Period"],
        value_vars=["Principal", "Interest"],
        var_name="Type",
        value_name="Amount"
    )

    payment_breakdown_chart = (
        alt.Chart(monthly_chart_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "Month:Q",
                title="Time",
                scale=alt.Scale(domain=[1, len(df)]),
                axis=alt.Axis(
                    values=year_marker_months,
                    labelExpr="'Y' + floor((datum.value - 1)/12 + 1)",
                    labelAngle=0,
                    grid=False
                )
            ),
            y=alt.Y("Amount:Q", title="Payment amount", stack="zero"),
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(
                    domain=["Principal", "Interest"],
                    range=["#4F81BD", "#C0504D"]
                ),
                legend=alt.Legend(title="")
            ),
            tooltip=[
                alt.Tooltip("Period:N", title="Period"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Amount:Q", title="Amount", format=",.2f")
            ]
        )
        .properties(height=320)
    )

    st.altair_chart(payment_breakdown_chart, use_container_width=True)

    # -----------------------------
    # Chart 3: Yearly view
    # -----------------------------
    st.subheader("Yearly view")

    yearly_chart_df = yearly_df.melt(
        id_vars=["Year", "YearLabel"],
        value_vars=["Principal", "Interest"],
        var_name="Type",
        value_name="Amount"
    )

    yearly_breakdown_chart = (
        alt.Chart(yearly_chart_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "Year:Q",
                title="Time",
                scale=alt.Scale(domain=[1, int(yearly_df["Year"].max())]),
                axis=alt.Axis(
                    values=yearly_df["Year"].tolist(),
                    labelExpr="'Y' + datum.value",
                    labelAngle=0,
                    grid=False
                )
            ),
            y=alt.Y("Amount:Q", title="Total paid in year", stack="zero"),
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(
                    domain=["Principal", "Interest"],
                    range=["#4F81BD", "#C0504D"]
                ),
                legend=alt.Legend(title="")
            ),
            tooltip=[
                alt.Tooltip("YearLabel:N", title="Year"),
                alt.Tooltip("Type:N", title="Type"),
                alt.Tooltip("Amount:Q", title="Amount", format=",.2f")
            ]
        )
        .properties(height=320)
    )

    st.altair_chart(yearly_breakdown_chart, use_container_width=True)

    # -----------------------------
    # Schedule table
    # -----------------------------
    if show_schedule:
        st.subheader("Amortization schedule")

        display_df = df.copy()
        display_df["Payment"] = display_df["Payment"].map(currency_fmt)
        display_df["Principal"] = display_df["Principal"].map(currency_fmt)
        display_df["Interest"] = display_df["Interest"].map(currency_fmt)
        display_df["Balance"] = display_df["Balance"].map(currency_fmt)

        st.dataframe(
            display_df[["Period", "Payment", "Principal", "Interest", "Balance"]],
            use_container_width=True,
            hide_index=True
        )
