import streamlit as st
import streamlit_antd_components as sac
import altair as alt
import calendar
from utils.byggesager_data import fetch_kategori_data, process_kategori_data, get_categories
import streamlit_shadcn_ui as ui


def get_byggesager_data():
    st.title("Kategori Visualiseringer")

    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Sagsbehandlingstid', tag='Sagsbehandlingstid'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'kategori_data_final_result' not in st.session_state:
            with st.spinner('Loading data...'):
                raw_data = fetch_kategori_data()
                processed_data = process_kategori_data(raw_data)
                st.session_state.kategori_data_final_result = processed_data

        final_result = st.session_state.kategori_data_final_result

        available_years = sorted(final_result['Year'].unique())

        if content_tabs == 'Sagsbehandlingstid':
            selected_year = st.selectbox("Vælg et år", available_years)

            year_data = final_result[final_result['Year'] == selected_year]

            categories = get_categories()

            selected_category = st.selectbox("Vælg en kategori", categories)

            st.write(f"## {selected_category} for {selected_year}")
            category_data = year_data[year_data['Kategori'] == selected_category]

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
                tooltip=[
                    alt.Tooltip('Måned:N', title='Måned'),
                    alt.Tooltip('Servicemål i procent:Q', title='Servicemål (%)', format='.2f')
                ]
            ).properties(
                width=600,
                height=300
            )
            st.altair_chart(bar_chart_service_goal, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
