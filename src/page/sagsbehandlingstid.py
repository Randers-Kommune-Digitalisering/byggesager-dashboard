import streamlit as st
import streamlit_antd_components as sac
import altair as alt
import calendar
from utils.byggesager_data import fetch_kategori_data, process_kategori_data, get_categories
import streamlit_shadcn_ui as ui
import pandas as pd


def get_byggesager_data():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Sagsbehandlingstid', tag='Sagsbehandlingstid', icon='bi bi-hourglass-split'),
            sac.TabsItem('Servicemål i %', tag='Servicemål i %', icon='bi bi-bar-chart'),
            sac.TabsItem('Glidende Gennemsnit', tag='Glidende Gennemsnit', icon='bi bi-bullseye'),
            sac.TabsItem('Historiske data', tag='Historiske data', icon='bi bi-clock-history'),
            sac.TabsItem('BI-Rapport', tag='BI-Rapport', icon='bi bi-file-earmark-bar-graph')
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

        if content_tabs == 'Sagsbehandlingstid':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='year_selection')
            year_data = final_result[final_result['Year'] == selected_year]

            categories = get_categories()
            if not categories:
                st.error("No categories available.")
                st.stop()

            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='category_selection')

            st.write(f"## {selected_category} for {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category]

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            avg_processing_time = category_data['Sagsbehandlingstid'].mean()
            avg_service_goal = category_data['Servicemål i procent'].mean()

            col1, col2 = st.columns([1, 1])

            with col1:
                ui.metric_card(
                    title="Gennemsnitlig Sagsbehandlingstid (dage)",
                    content=f"{avg_processing_time:.2f}",
                    description="Gennemsnitlig tid for sagsbehandling i dage."
                )

            with col2:
                ui.metric_card(
                    title="Gennemsnitligt Servicemål (%)",
                    content=f"{avg_service_goal:.2f}",
                    description="Gennemsnitligt opfyldelse af servicemål i procent."
                )

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            st.write("### Gennemsnitlig Sagsbehandlingstid pr. måned")
            bar_chart_processing_time = alt.Chart(monthly_data).mark_bar().encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
                y=alt.Y('Sagsbehandlingstid:Q', title='Gennemsnitlig Sagsbehandlingstid (dage)'),
                color=alt.Color('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', scale=alt.Scale(scheme='blues')),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            ).properties(
                width=600,
                height=300
            )
            st.altair_chart(bar_chart_processing_time, use_container_width=True)

            st.write("### Gennemsnitligt Servicemål (%) pr. måned")
            bar_chart_service_goal = alt.Chart(monthly_data).mark_bar().encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
                y=alt.Y('Servicemål i procent:Q', title='Gennemsnitligt Servicemål (%)'),
                color=alt.Color('Servicemål i procent:Q', title='Servicemål (%)', scale=alt.Scale(scheme='blues')),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            ).properties(
                width=600,
                height=300
            )
            st.altair_chart(bar_chart_service_goal, use_container_width=True)

        elif content_tabs == 'Servicemål i %':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='dual_axis_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]

            categories = get_categories()
            if not categories:
                st.error("No categories available.")
                st.stop()

            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='dual_axis_category_selection')

            st.write(f"## Sagsbehandlingstid og servicemål pr. måned for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category]

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            monthly_data = category_data.groupby('Måned', sort=False).mean(numeric_only=True).reset_index()
            monthly_data['SortOrder'] = monthly_data['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_data = monthly_data.sort_values('SortOrder')

            base = alt.Chart(monthly_data).encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
            )

            bar = base.mark_bar().encode(
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            )

            line = base.mark_line(point=True).encode(
                y=alt.Y('Servicemål i procent:Q', title='Servicemål (%)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

        elif content_tabs == 'Glidende Gennemsnit':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='rolling_avg_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]

            categories = get_categories()
            if not categories:
                st.error("No categories available.")
                st.stop()

            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key='rolling_avg_service_goal_category_selection')

            st.write(f"## Gennemsnitligt Servicemål (12 måneder) for {selected_category} i {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category].copy()

            if category_data.empty:
                st.warning("No data available for the selected category and year.")
                return

            category_data['Date'] = pd.to_datetime(category_data['Year'].astype(str) + '-' + category_data['Måned'], format='%Y-%b')

            category_data['RollingAvgServiceGoal'] = category_data['Servicemål i procent'].rolling(window=12, min_periods=1).mean()

            avg_rolling_service_goal = category_data['RollingAvgServiceGoal'].iloc[-12:].mean()

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
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            )

            line = base.mark_line(point=True).encode(
                y=alt.Y('RollingAvgServiceGoal:Q', title='Gennemsnitligt Servicemål (%)', axis=alt.Axis(titleColor='orange')),
                color=alt.value('orange'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('RollingAvgServiceGoal:Q', title='Gennemsnitligt Servicemål (%)', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=600,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

        elif content_tabs == 'Historiske data':
            categories = get_categories()
            if not categories:
                st.error("No categories available.")
                st.stop()

            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key="historisk_kategori_linje")

            st.write(f"## Sagsbehandlingstid og servicemål pr. måned – sammenligning for {selected_category} (seneste år)")

            category_data = final_result[final_result['Kategori'] == selected_category].copy()
            if category_data.empty:
                st.warning("Ingen data for valgt kategori.")
                return

            monthly_bar = category_data.groupby(['Year', 'Måned'], as_index=False).mean(numeric_only=True)
            monthly_bar['SortOrder'] = monthly_bar['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_bar = monthly_bar.sort_values(['Year', 'SortOrder'])

            bar = alt.Chart(monthly_bar).mark_bar().encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                color=alt.Color('Year:N', title='År', scale=alt.Scale(scheme='set1')),
                tooltip=[
                    alt.Tooltip('Year:N', title='År'),
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f')
                ]
            )

            line = alt.Chart(monthly_bar).mark_line(point=True).encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
                y=alt.Y('Servicemål i procent:Q', title='Servicemål (%)', axis=alt.Axis(titleColor='orange')),
                color=alt.Color('Year:N', title='År', scale=alt.Scale(scheme='set1')),
                tooltip=[
                    alt.Tooltip('Year:N', title='Årr'),
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=900,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

        elif content_tabs == 'BI-Rapport':
            selected_year = st.selectbox("Vælg et år", available_years, help='Vælg et år for at se data', key='bi_rapport_year_selection')
            year_data = final_result[final_result['Year'] == selected_year]

            categories = get_categories()
            if not categories:
                st.error("No categories available.")
                st.stop()

            selected_category = st.selectbox("Vælg en kategori", categories, help='Vælg en kategori for at se data', key="bi_rapport_kategori")

            st.write(f"## Sagsbehandlingstid, Servicemål og Glidende Gennemsnit ({selected_category}) i {selected_year}")

            category_data = final_result[final_result['Kategori'] == selected_category].copy()
            if category_data.empty:
                st.warning("Ingen data for valgt kategori.")
                return

            category_data = year_data[year_data['Kategori'] == selected_category]
            category_data['Date'] = pd.to_datetime(category_data['Year'].astype(str) + '-' + category_data['Måned'], format='%Y-%b')
            category_data['Glidende Gennemsnit (%)'] = category_data['Servicemål i procent'].rolling(window=12, min_periods=1).mean()

            monthly_bar = category_data.groupby('Måned', as_index=False).mean(numeric_only=True)
            monthly_bar['SortOrder'] = monthly_bar['Måned'].apply(lambda x: list(calendar.month_abbr).index(x))
            monthly_bar = monthly_bar.sort_values('SortOrder')

            base = alt.Chart(monthly_bar).encode(
                x=alt.X('Måned:N', title='Måned', sort=list(calendar.month_abbr)[1:]),
            )

            bar = base.mark_bar().encode(
                y=alt.Y('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)'),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Sagsbehandlingstid:Q', title='Sagsbehandlingstid (dage)', format='.2f'),
                ]
            )

            melted = monthly_bar.melt(id_vars=['Måned', 'SortOrder'], value_vars=['Servicemål i procent', 'Glidende Gennemsnit (%)'],
                                      var_name='Type', value_name='Value')

            line = alt.Chart(melted).mark_line(point=True).encode(
                x=alt.X('Måned:N', sort=list(calendar.month_abbr)[1:]),
                y=alt.Y('Value:Q', title='Servicemål (%) og Glidende Gennemsnit (%)'),
                color=alt.Color('Type:N', scale=alt.Scale(domain=['Servicemål i procent', 'Glidende Gennemsnit (%)', 'Sagsbehandlingstid'],
                                range=['orange', 'green', 'blue'])),
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Type:N', title='Type'),
                    alt.Tooltip('Value:Q', title='Værdi', format='.2f')
                ]
            )

            dual_axis_chart = alt.layer(bar, line).resolve_scale(
                y='independent'
            ).properties(
                width=900,
                height=400
            )

            st.altair_chart(dual_axis_chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
