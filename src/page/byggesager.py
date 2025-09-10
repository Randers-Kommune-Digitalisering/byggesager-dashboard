import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from utils.database_connection import get_byggesager_db
import streamlit_antd_components as sac

db_client = get_byggesager_db()


def get_byggesager_overview():
    content_tabs = sac.tabs([
        sac.TabsItem('Antal Modtagne & Afgjorte byggesager', tag='Modtagne & Afgjorte', icon='bi bi-building'),
        sac.TabsItem('Antal Modtagne Byggesager', tag='Modtagne Byggesager', icon='bi bi-building-add'),
        sac.TabsItem('Antal Afgjorte Byggesager', tag='Afgjorte Byggesager', icon='bi bi-building-fill-check'),
        sac.TabsItem('Antal Afgjorte Byggesager opdelt efter Afgørelsestype', tag='Afgørelsestype', icon='bi bi-buildings'),
        sac.TabsItem('Antal Modtagede Byggesager opdelt efter Type', tag='Type', icon='bi bi-buildings-fill'),
    ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'byggesager_data' not in st.session_state:
            with st.spinner('Indlæser byggesagsdata...'):
                query_modtagede = (
                    'SELECT "Dato", "Gruppering", "Antal" '
                    'FROM byggesager_modtagede'
                )
                result_modtagede = db_client.execute_sql(query_modtagede)
                df_modtagede = pd.DataFrame(result_modtagede, columns=["Dato", "Gruppering", "Antal"])
                df_modtagede["Type"] = "Modtagede"

                query_afgjorte = (
                    'SELECT "Dato", "Gruppering", "Beslutningstype", "Antal" '
                    'FROM byggesager_afgjorte'
                )
                result_afgjorte = db_client.execute_sql(query_afgjorte)
                df_afgjorte = pd.DataFrame(result_afgjorte, columns=["Dato", "Gruppering", "Beslutningstype", "Antal"])
                df_afgjorte["Type"] = "Afgjorte"

                df_modtagede["Beslutningstype"] = None
                df = pd.concat([df_modtagede, df_afgjorte], ignore_index=True)
                st.session_state.byggesager_data = df
        df = st.session_state.byggesager_data.copy()

        df["Dato"] = pd.to_datetime(df["Dato"], errors='coerce')
        df["År"] = df["Dato"].dt.year.astype(str)
        df["Måned"] = df["Dato"].dt.month
        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
        }
        df["MånedNavn"] = df["Måned"].map(month_map)
        df["Antal"] = pd.to_numeric(df["Antal"], errors="coerce")

        available_years = sorted(df["År"].unique())
        selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 1)

        if content_tabs == 'Antal Modtagne & Afgjorte byggesager':
            chart_df = df[df["År"] == selected_year].dropna(subset=["MånedNavn", "Type", "Antal"])
            chart_df = chart_df.groupby(["Måned", "MånedNavn", "Type"], as_index=False)["Antal"].sum()
            month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
            chart_df["MånedNavn"] = pd.Categorical(chart_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal modtagne og afgjorte byggesager - {selected_year}", divider="gray")
            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                y=alt.Y('Antal:Q', title='Antal byggesager'),
                xOffset=alt.XOffset('Type:N', title='Type'),
                color=alt.Color('Type:N', title='Type'),
                tooltip=[
                    alt.Tooltip('MånedNavn:N', title='Måned'),
                    alt.Tooltip('Type:N', title='Type'),
                    alt.Tooltip('Antal:Q', title='Antal')
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = chart_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
            export_df = export_df[["Periode", "Type", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Modtagne & Afgjorte Byggesager')
            output.seek(0)

            st.download_button(
                label="Eksporter Modtagne & Afgjorte byggesager til Excel",
                data=output,
                file_name=f"byggesager_modtagne_afgjorte_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Modtagne Byggesager':
            modtagne_df = df[(df["År"] == selected_year) & (df["Type"] == "Modtagede")].dropna(subset=["MånedNavn", "Antal"])
            modtagne_df = modtagne_df.groupby(["Måned", "MånedNavn"], as_index=False)["Antal"].sum()
            month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
            modtagne_df["MånedNavn"] = pd.Categorical(modtagne_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Modtagne Byggesager - {selected_year}", divider="gray")
            chart = alt.Chart(modtagne_df).mark_bar().encode(
                x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                y=alt.Y('Antal:Q', title='Antal Modtagne Byggesager'),
                tooltip=[
                    alt.Tooltip('MånedNavn:N', title='Måned'),
                    alt.Tooltip('Antal:Q', title='Antal')
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = modtagne_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
            export_df = export_df[["Periode", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Modtagne')
            output.seek(0)

            st.download_button(
                label="Eksporter Modtagne Byggesager til Excel",
                data=output,
                file_name=f"byggesager_modtagne_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Afgjorte Byggesager':
            afgjorte_df = df[(df["År"] == selected_year) & (df["Type"] == "Afgjorte")].dropna(subset=["MånedNavn", "Antal"])
            afgjorte_df = afgjorte_df.groupby(["Måned", "MånedNavn"], as_index=False)["Antal"].sum()
            month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
            afgjorte_df["MånedNavn"] = pd.Categorical(afgjorte_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Afgjorte Byggesager - {selected_year}", divider="gray")
            chart = alt.Chart(afgjorte_df).mark_bar().encode(
                x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                y=alt.Y('Antal:Q', title='Antal Afgjorte Byggesager'),
                tooltip=[
                    alt.Tooltip('MånedNavn:N', title='Måned'),
                    alt.Tooltip('Antal:Q', title='Antal')
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = afgjorte_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
            export_df = export_df[["Periode", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Afgjorte')
            output.seek(0)

            st.download_button(
                label="Eksporter Afgjorte Byggesager til Excel",
                data=output,
                file_name=f"byggesager_afgjorte_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Afgjorte Byggesager opdelt efter Afgørelsestype':
            afgjorte_type_df = df[(df["År"] == selected_year) & (df["Type"] == "Afgjorte")].dropna(subset=["MånedNavn", "Beslutningstype", "Antal"])
            afgjorte_type_df = afgjorte_type_df.groupby(["Måned", "MånedNavn", "Beslutningstype"], as_index=False)["Antal"].sum()
            month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
            afgjorte_type_df["MånedNavn"] = pd.Categorical(afgjorte_type_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Afgjorte Byggesager opdelt efter Afgørelsestype - {selected_year}", divider="gray")
            chart = alt.Chart(afgjorte_type_df).mark_bar().encode(
                x=alt.X("MånedNavn:N", title="Måned", sort=month_order),
                y=alt.Y("Antal:Q", title="Antal"),
                color=alt.Color("Beslutningstype:N", title="Afgørelsestype"),
                tooltip=[
                    alt.Tooltip("MånedNavn:N", title="Måned"),
                    alt.Tooltip("Beslutningstype:N", title="Afgørelsestype"),
                    alt.Tooltip("Antal:Q", title="Antal")
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = afgjorte_type_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
            export_df = export_df[["Periode", "Beslutningstype", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Afgørelsestype')
            output.seek(0)

            st.download_button(
                label="Eksporter Afgørelsestyper til Excel",
                data=output,
                file_name=f"byggesager_afgorelsetype_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Modtagede Byggesager opdelt efter Type':
            modtagede_type_df = df[(df["År"] == selected_year) & (df["Type"] == "Modtagede")].dropna(subset=["MånedNavn", "Gruppering", "Antal"])
            modtagede_type_df = modtagede_type_df.groupby(["Måned", "MånedNavn", "Gruppering"], as_index=False)["Antal"].sum()
            month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
            modtagede_type_df["MånedNavn"] = pd.Categorical(modtagede_type_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Modtagede Byggesager opdelt efter Type - {selected_year}", divider="gray")
            chart = alt.Chart(modtagede_type_df).mark_bar().encode(
                x=alt.X("MånedNavn:N", title="Måned", sort=month_order),
                y=alt.Y("Antal:Q", title="Antal"),
                color=alt.Color("Gruppering:N", title="Type"),
                tooltip=[
                    alt.Tooltip("MånedNavn:N", title="Måned"),
                    alt.Tooltip("Gruppering:N", title="Type"),
                    alt.Tooltip("Antal:Q", title="Antal")
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = modtagede_type_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
            export_df = export_df[["Periode", "Gruppering", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Type')
            output.seek(0)

            st.download_button(
                label="Eksporter Modtagede Byggesager Typer til Excel",
                data=output,
                file_name=f"byggesager_type_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

    except Exception as e:
        st.error(f'Fejl ved hentning af byggesagsdata: {e}')
    finally:
        db_client.close_connection()
