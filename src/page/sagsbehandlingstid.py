import streamlit as st
import streamlit_antd_components as sac
import altair as alt
import calendar
from utils.byggesager_data import fetch_glidende_gennemsnit_data, fetch_monthly_data, process_glidende_gennemsnit_data, process_monthly_data, get_categories
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
        historical_data = fetch_monthly_data()
        if historical_data is None:
            st.error("Failed to fetch data from the database.")
            st.stop()

        final_result = process_monthly_data(historical_data)
        if final_result is None or final_result.empty:
            st.error("Failed to process data or no data available.")
            st.stop()

        glidende_gennemsnit_raw = fetch_glidende_gennemsnit_data()
        glidende_result = process_glidende_gennemsnit_data(glidende_gennemsnit_raw)

        available_years = sorted(final_result['Year'].unique())
        categories = get_categories()
        if not categories:
            st.error("No categories available.")
            st.stop()

        latest_year_index = max(len(available_years) - 1, 0)

        if content_tabs == 'Servicemålprocent':
            selected_year = st.selectbox("Vælg et år", available_years, index=latest_year_index, help='Vælg et år for at se data', key='service_goal_percent_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]
            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='service_goal_percent_category_selection')

            st.write(f"## Servicemålprocent pr. måned og glidende gennemsnit for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category].copy()

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            line_data = glidende_result.copy()
            if not line_data.empty:
                line_data = line_data[(line_data["Year"] == selected_year) & (line_data["Kategori"] == selected_category)].copy()

            avg_glidende_service_goal = None
            if glidende_result is not None and not glidende_result.empty:
                _cat_all = glidende_result[glidende_result["Kategori"] == selected_category].sort_values("Til Dato")
                if not _cat_all.empty:
                    avg_glidende_service_goal = _cat_all["Servicemål i procent"].iloc[-1]

            col1 = st.columns(1)[0]
            with col1:
                ui.metric_card(
                    title="Seneste glidende gennemsnit Servicemålprocent (%)",
                    content=f"{avg_glidende_service_goal:.2f}" if avg_glidende_service_goal is not None else "—",
                    description="Seneste glidende gennemsnit servicemålprocent fra databasen."
                )

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            if line_data is not None and not line_data.empty:
                line_data['SortOrder'] = line_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
                line_data = line_data.sort_values('SortOrder')

            base_x = alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:])

            bar = alt.Chart(monthly_data).mark_bar().encode(
                x=base_x,
                y=alt.Y('Servicemål i procent:Q', title='Servicemål (%)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            )

            line = alt.Chart(line_data).mark_line(point=True).encode(
                x=base_x,
                y=alt.Y('Servicemål i procent:Q', title='Glidende gennemsnit (%)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Glidende gennemsnit (%)', format='.2f'),
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(y='independent').properties(width=600, height=400)
            st.altair_chart(dual_axis_chart, width="stretch")

            export_df = monthly_data[['Måned', 'Servicemål i procent']].rename(columns={'Servicemål i procent': 'Servicemål (%)'})
            if line_data is not None and not line_data.empty:
                export_line = line_data[['Måned', 'Servicemål i procent']].rename(columns={'Servicemål i procent': 'Glidende gennemsnit (%)'})
                export_df = export_df.merge(export_line, on='Måned', how='left')
            else:
                export_df['Glidende gennemsnit (%)'] = pd.NA

            export_df.insert(0, "Periode", export_df["Måned"].astype(str) + " " + str(selected_year))
            export_df.insert(1, "Kategori", selected_category)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Servicemålprocent')
                worksheet = writer.sheets['Servicemålprocent']
                for i, col in enumerate(export_df.columns):
                    max_len = max(export_df[col].astype(str).map(len).max(), len(col)) + 2
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
            selected_year = st.selectbox("Vælg et år", available_years, index=latest_year_index, help='Vælg et år for at se data', key='processing_time_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]
            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='processing_time_category_selection')

            st.write(f"## Sagsbehandlingstid pr. måned og glidende gennemsnit for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category].copy()

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            line_data = glidende_result.copy()
            if not line_data.empty:
                line_data = line_data[(line_data["Year"] == selected_year) & (line_data["Kategori"] == selected_category)].copy()

            avg_glidende_processing_time = None
            if glidende_result is not None and not glidende_result.empty:
                _cat_all = glidende_result[glidende_result["Kategori"] == selected_category].sort_values("Til Dato")
                if not _cat_all.empty:
                    avg_glidende_processing_time = _cat_all["Sagsbehandlingstid"].iloc[-1]

            col1 = st.columns(1)[0]
            with col1:
                ui.metric_card(
                    title="Seneste glidende gennemsnit for Sagsbehandlingstid (dage)",
                    content=f"{avg_glidende_processing_time:.2f}" if avg_glidende_processing_time is not None else "—",
                    description="Seneste glidende gennemsnit fra databasen."
                )

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            if line_data is not None and not line_data.empty:
                line_data['SortOrder'] = line_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
                line_data = line_data.sort_values('SortOrder')

            base_x = alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:])

            bar = alt.Chart(monthly_data).mark_bar().encode(
                x=base_x,
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            )

            line = alt.Chart(line_data).mark_line(point=True).encode(
                x=base_x,
                y=alt.Y('Sagsbehandlingstid:Q', title='Glidende gennemsnit (dage)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Glidende gennemsnit (dage)', format='.2f'),
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(y='independent').properties(width=600, height=400)
            st.altair_chart(dual_axis_chart, width="stretch")

            export_df = monthly_data[['Måned', 'Sagsbehandlingstid']].rename(columns={'Sagsbehandlingstid': 'Sagsbehandlingstid (dage)'})
            if line_data is not None and not line_data.empty:
                export_line = line_data[['Måned', 'Sagsbehandlingstid']].rename(columns={'Sagsbehandlingstid': 'Glidende gennemsnit (dage)'})
                export_df = export_df.merge(export_line, on='Måned', how='left')
            else:
                export_df['Glidende gennemsnit (dage)'] = pd.NA

            export_df.insert(0, "Periode", export_df["Måned"].astype(str) + " " + str(selected_year))
            export_df.insert(1, "Kategori", selected_category)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Sagsbehandlingstid')
                worksheet = writer.sheets['Sagsbehandlingstid']
                for i, col in enumerate(export_df.columns):
                    max_len = max(export_df[col].astype(str).map(len).max(), len(col)) + 2
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
