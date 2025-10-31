import altair as alt
import pandas as pd

from utils.byggesager_data import get_month_order


def sag_count_bar_chart_with_lines(dataframe: pd.DataFrame, selected_year: int) -> alt.Chart:
    years_to_plot = [int(selected_year), int(selected_year - 1), int(selected_year - 2)]
    filtered_df = dataframe[dataframe["År"].isin(years_to_plot)]
    filtered_df["ChartType"] = filtered_df["År"].apply(
        lambda y: "Bar" if y == selected_year else "Line"
    )

    color_scale = alt.Scale(
        domain=years_to_plot,
        range=["#1f77b4", "#d62728", "#2ca02c"]  # Altair default colors (in reversed order)
    )

    base = alt.Chart(filtered_df).encode(
        x=alt.X("MånedNavn:N", title="Måned", sort=get_month_order()),
        y=alt.Y("Antal:Q", title="Antal"),
        color=alt.Color("År:N", title="År", scale=color_scale),
        tooltip=[
            alt.Tooltip("År:Q", title="År"),
            alt.Tooltip("MånedNavn:N", title="Måned"),
            alt.Tooltip("Antal:N", title="Antal")
        ]
    )

    bar = base.transform_filter(
        alt.datum.ChartType == "Bar"
    ).mark_bar()

    line = base.transform_filter(
        alt.datum.ChartType == "Line"
    ).mark_line()

    chart = bar + line
    return chart
