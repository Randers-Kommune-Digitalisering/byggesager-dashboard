import streamlit as st
import altair as alt
import calendar
from utils.byggesager_data import fetch_kategori_data, process_kategori_data, get_categories
import streamlit_shadcn_ui as ui
import pandas as pd
from io import BytesIO


def render_sagsbehandling_tabs() -> str:
    """Render full-width handmade dashboard tabs."""

    if "sagsbehandling_active_tab" not in st.session_state:
        st.session_state.sagsbehandling_active_tab = "Sagsbehandlingstid"

    selected_tab = st.session_state.sagsbehandling_active_tab

    st.markdown(
        """
<style>
/* Wrapper around both tabs */
.st-key-sagsbehandling_tabs {
    width: 100%;
    margin-bottom: 1.5rem;
}

/* Space between the two tab columns */
.st-key-sagsbehandling_tabs [data-testid="stHorizontalBlock"] {
    gap: 3rem;
}

/* Make each keyed tab container fill its column */
.st-key-processing_time_tab,
.st-key-service_goal_tab {
    width: 100%;
}

/* Make Streamlit's button wrapper full width */
.st-key-processing_time_tab [data-testid="stButton"],
.st-key-service_goal_tab [data-testid="stButton"] {
    width: 100%;
    margin: 0;
}

/* Shared appearance for both tab buttons */
.st-key-processing_time_tab button,
.st-key-service_goal_tab button {
    width: 100% !important;
    min-height: 86px;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 12px 10px;
    margin: 0;

    background-color: transparent !important;
    color: #34343c !important;

    border: none !important;
    border-bottom: 2px solid #dddddd !important;
    border-radius: 0 !important;

    box-shadow: none !important;
}

/* Remove Streamlit focus styling */
.st-key-processing_time_tab button:focus,
.st-key-service_goal_tab button:focus,
.st-key-processing_time_tab button:active,
.st-key-service_goal_tab button:active {
    box-shadow: none !important;
    outline: none !important;
}

/* Hover appearance */
.st-key-processing_time_tab button:hover,
.st-key-service_goal_tab button:hover {
    background-color: #fafafa !important;
    color: #34343c !important;
}

/* Text row inside each tab */
.st-key-processing_time_tab button p,
.st-key-service_goal_tab button p {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 9px;

    margin: 0;

    color: #34343c !important;
    font-size: 20px;
    font-weight: 400;
    line-height: 1.3;
    text-align: center;
    white-space: normal;
}

/* Bootstrap icon before each tab title */
.st-key-processing_time_tab button p::before,
.st-key-service_goal_tab button p::before {
    content: "";

    display: inline-block;
    width: 20px;
    height: 20px;
    flex: 0 0 20px;

    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}

/* Hourglass icon */
.st-key-processing_time_tab button p::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/hourglass-split.svg"
    );
}

/* Bar-chart icon */
.st-key-service_goal_tab button p::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/bar-chart.svg"
    );
}

/* Shared grey pill */
.st-key-processing_time_tab button p::after,
.st-key-service_goal_tab button p::after {
    display: inline-block;

    padding: 3px 10px;

    background-color: #f1f1f1;
    border: 1px solid #d1d1d1;
    border-radius: 999px;

    color: #55555d;
    font-size: 13px;
    font-weight: 400;
    line-height: 1.2;
    white-space: nowrap;
}

/* Sagsbehandlingstid pill text */
.st-key-processing_time_tab button p::after {
    content: "Sagsbehandlingstid";
}

/* Servicemålprocent pill text */
.st-key-service_goal_tab button p::after {
    content: "Servicemålprocent";
}

/* Responsive layout */
@media (max-width: 850px) {
    .st-key-sagsbehandling_tabs [data-testid="stHorizontalBlock"] {
        gap: 0.75rem;
    }

    .st-key-processing_time_tab button,
    .st-key-service_goal_tab button {
        min-height: 72px;
    }

    .st-key-processing_time_tab button p,
    .st-key-service_goal_tab button p {
        font-size: 17px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    # Dark underline on the selected tab.
    if selected_tab == "Sagsbehandlingstid":
        st.markdown(
            """
<style>
.st-key-processing_time_tab button {
    border-bottom-color: #2f2f2f !important;
}
</style>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<style>
.st-key-service_goal_tab button {
    border-bottom-color: #2f2f2f !important;
}
</style>
""",
            unsafe_allow_html=True,
        )

    def select_tab(tab_name: str) -> None:
        st.session_state.sagsbehandling_active_tab = tab_name

    with st.container(key="sagsbehandling_tabs"):
        processing_column, service_column = st.columns(
            2,
            gap="large",
        )

        with processing_column:
            with st.container(key="processing_time_tab"):
                st.button(
                    "Sagsbehandlingstid",
                    key="processing_time_tab_button",
                    use_container_width=True,
                    on_click=select_tab,
                    args=("Sagsbehandlingstid",),
                )

        with service_column:
            with st.container(key="service_goal_tab"):
                st.button(
                    "Servicemålprocent",
                    key="service_goal_tab_button",
                    use_container_width=True,
                    on_click=select_tab,
                    args=("Servicemålprocent",),
                )

    return st.session_state.sagsbehandling_active_tab


def get_sagsbehandlingstid_overview():
    content_tabs = render_sagsbehandling_tabs()

    try:

        historical_data = fetch_kategori_data()
        if historical_data is None:
            st.error("Failed to fetch data from the database.")
            st.stop()

        final_result = process_kategori_data(historical_data)
        if final_result is None or final_result.empty:
            st.error("Failed to process data or no data available.")
            st.stop()

        available_years = sorted(final_result['Year'].unique())
        categories = get_categories()
        if not categories:
            st.error("No categories available.")
            st.stop()

        if content_tabs == 'Servicemålprocent':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='service_goal_percent_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]
            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='service_goal_percent_category_selection')

            st.write(f"## Servicemålprocent pr. måned og glidende gennemsnit for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category].copy()

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            category_data['Date'] = pd.to_datetime(category_data['Year'].astype(str) + '-' + category_data['Måned'], format='%Y-%b')
            category_data = category_data.sort_values('Date')
            category_data['GlidendeGennemsnitServiceMål'] = category_data['Servicemål i procent'].rolling(window=12, min_periods=1).mean()
            avg_rolling_service_goal = category_data['GlidendeGennemsnitServiceMål'].iloc[-12:].mean()

            col1 = st.columns(1)[0]
            with col1:
                ui.metric_card(
                    title="Gennemsnitligt Servicemål (12 måneder) (%)",
                    content=f"{avg_rolling_service_goal:.2f}",
                    description="Gennemsnitligt opfyldelse af servicemål i procent for de seneste 12 måneder."
                )

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            base = alt.Chart(monthly_data).encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:])
            )

            bar = base.mark_bar().encode(
                y=alt.Y('Servicemål i procent:Q', title='Servicemål (%)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            )

            line = base.mark_line(point=True).encode(
                y=alt.Y('GlidendeGennemsnitServiceMål:Q', title='Glidende gennemsnit (%)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('GlidendeGennemsnitServiceMål:Q', title='Glidende gennemsnit (%)', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

            export_df = category_data.copy()
            export_df["Periode"] = export_df["Måned"].astype(str) + " " + export_df["Year"].astype(str)
            export_df = export_df[["Periode", "Kategori", "Servicemål i procent", "GlidendeGennemsnitServiceMål"]]
            export_df.rename(columns={
                "Servicemål i procent": "Servicemål (%)",
                "GlidendeGennemsnitServiceMål": "Glidende gennemsnit (%)"
            }, inplace=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Servicemålprocent')
                worksheet = writer.sheets['Servicemålprocent']
                for i, col in enumerate(export_df.columns):
                    max_len = max(
                        export_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
            output.seek(0)

            st.download_button(
                label="Eksporter Servicemålprocent Data til Excel",
                data=output,
                file_name=f"servicemaalprocent_{selected_category}_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

        elif content_tabs == 'Sagsbehandlingstid':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='processing_time_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]
            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='processing_time_category_selection')

            st.write(f"## Sagsbehandlingstid pr. måned og glidende gennemsnit for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category].copy()

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            category_data['Date'] = pd.to_datetime(category_data['Year'].astype(str) + '-' + category_data['Måned'], format='%Y-%b')
            category_data['GlidendeGennemsnitSagsbehandlingstid'] = category_data['Sagsbehandlingstid'].rolling(window=12, min_periods=1).mean()
            avg_rolling_processing_time = category_data['GlidendeGennemsnitSagsbehandlingstid'].iloc[-12:].mean()

            col1 = st.columns(1)[0]
            with col1:
                ui.metric_card(
                    title="Gennemsnitlig Sagsbehandlingstid (12 måneder) (dage)",
                    content=f"{avg_rolling_processing_time:.2f}",
                    description="Gennemsnitlig sagsbehandlingstid i dage for de seneste 12 måneder."
                )

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            base = alt.Chart(monthly_data).encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:])
            )

            bar = base.mark_bar().encode(
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            )

            line = base.mark_line(point=True).encode(
                y=alt.Y('GlidendeGennemsnitSagsbehandlingstid:Q', title='Glidende gennemsnit (dage)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('GlidendeGennemsnitSagsbehandlingstid:Q', title='Glidende gennemsnit (dage)', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

            export_df = category_data.copy()
            export_df["Periode"] = export_df["Måned"].astype(str) + " " + export_df["Year"].astype(str)
            export_df = export_df[["Periode", "Kategori", "Sagsbehandlingstid", "GlidendeGennemsnitSagsbehandlingstid"]]
            export_df.rename(columns={
                "Sagsbehandlingstid": "Sagsbehandlingstid (dage)",
                "GlidendeGennemsnitSagsbehandlingstid": "Glidende gennemsnit (dage)"
            }, inplace=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Sagsbehandlingstid')
                worksheet = writer.sheets['Sagsbehandlingstid']
                for i, col in enumerate(export_df.columns):
                    max_len = max(
                        export_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
            output.seek(0)

            st.download_button(
                label="Eksporter Sagsbehandlingstid Data til Excel",
                data=output,
                file_name=f"sagsbehandlingstid_{selected_category}_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
