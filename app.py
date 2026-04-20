st.subheader("Balance over time")

year_positions = [(y - 1) * 12 + 1 for y in yearly_df["Year"]]

balance_chart = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "Month:Q",
            title="Time",
            axis=alt.Axis(
                values=year_positions,  # 👈 only year markers
                labelExpr="'Y' + floor((datum.value - 1)/12 + 1)",
                labelAngle=0
            )
        ),
        y=alt.Y(
            "Balance:Q",
            title="Remaining balance"
        ),
        tooltip=[
            alt.Tooltip("Month:Q", title="Month"),
            alt.Tooltip("Balance:Q", title="Balance", format=",.2f")
        ]
    )
    .properties(height=320)
)

st.altair_chart(balance_chart, use_container_width=True)
