import streamlit as st
import streamlit_antd_components as sac
import altair as alt
import calendar
from utils.byggesager_data import fetch_kategori_data, process_kategori_data, get_categories
import streamlit_shadcn_ui as ui
import pandas as pd
from io import BytesIO


def get_sagsbehandlingstid_overview():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Sagsbehandlingstid', tag='Sagsbehandlingstid', icon='bi bi-hourglass-split'),
            sac.TabsItem('Servicemålprocent', tag='Servicemålprocent', icon='bi bi-bar-chart'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

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
