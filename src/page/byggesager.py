import altair as alt
import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
import streamlit_shadcn_ui as ui

from io import BytesIO

from utils.byggesager_data import get_month_map, get_month_order
from utils.chart import sag_count_bar_chart_with_lines
from data import get_modtagne_byggesager, get_afgjorte_byggesager


def get_byggesager_overview():
    content_tabs = sac.tabs([
        sac.TabsItem('Antal Modtagne & Afgjorte byggesager', tag='Modtagne & Afgjorte', icon='bi bi-building'),
        sac.TabsItem('Antal Modtagne Byggesager', tag='Modtagne Byggesager', icon='bi bi-building-add'),
        sac.TabsItem('Antal Afgjorte Byggesager', tag='Afgjorte Byggesager', icon='bi bi-building-fill-check'),
        sac.TabsItem('Antal Modtagede Byggesager opdelt efter Type', tag='Type', icon='bi bi-buildings-fill'),
        sac.TabsItem('Antal Afgjorte Byggesager opdelt efter Afgørelsestype', tag='Afgørelsestype', icon='bi bi-buildings'),
    ], color='dark', size='md', position='top', align='start', use_container_width=True)

    if 'byggesager_data' not in st.session_state:
        with st.spinner('Indlæser byggesagsdata...'):
            df_modtagede = get_modtagne_byggesager(
                grupper=[
                    "Industri og lager",
                    "Sekundært byggeri",
                    "Erhverv",
                    "Enfamiliehuse",
                    "Etageejendomme"
                ],
                start_year=2020
            )
            df_modtagede["Type"] = "Modtagede"

            df_afgjorte = get_afgjorte_byggesager(
                grupper=[
                    "Industri og lager",
                    "Sekundært byggeri",
                    "Erhverv",
                    "Enfamiliehuse",
                    "Etageejendomme"
                ],
                start_year=2020
            )
            df_afgjorte["Type"] = "Afgjorte"

            df = pd.concat([df_modtagede, df_afgjorte], ignore_index=True)
            st.session_state.byggesager_data = df

    df = st.session_state.byggesager_data.copy()
    month_map = get_month_map()
    df["MånedNavn"] = df["Måned"].map(month_map)

    available_years = sorted(df["År"].unique())[2:]
    if content_tabs == 'Antal Modtagne & Afgjorte byggesager':
        available_years.append("Alle år")
        selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 2)
    else:
        selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 1)

    if content_tabs == 'Antal Modtagne & Afgjorte byggesager':
        if selected_year == "Alle år":
            chart_df = df.dropna(subset=["År", "Type", "Antal"])
            chart_df = chart_df.groupby(["År", "Type"], as_index=False)["Antal"].sum()
            total_modtagne = int(chart_df[chart_df["Type"] == "Modtagede"]["Antal"].sum())
            total_afgjorte = int(chart_df[chart_df["Type"] == "Afgjorte"]["Antal"].sum())

            col1, col2 = st.columns([1, 1])
            with col1:
                ui.metric_card(
                    title="Samlet antal Modtagne byggesager",
                    content=total_modtagne,
                    description="Modtagne byggesager (alle år)."
                )
            with col2:
                ui.metric_card(
                    title="Samlet antal Afgjorte byggesager",
                    content=total_afgjorte,
                    description="Afgjorte byggesager (alle år)."
                )

            st.header("Antal modtagne og afgjorte byggesager - Alle år", divider="gray")
            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('År:N', title='År'),
                y=alt.Y('Antal:Q', title='Antal byggesager'),
                xOffset=alt.XOffset('Type:N', title='Type'),
                color=alt.Color('Type:N', title='Type'),
                tooltip=[
                    alt.Tooltip('År:N', title='År'),
                    alt.Tooltip('Type:N', title='Type'),
                    alt.Tooltip('Antal:Q', title='Antal')
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, width="stretch")

            export_df = chart_df.copy()
            export_df["Periode"] = export_df["År"].astype(str)
            export_df = export_df[["Periode", "Type", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Modtagne & Afgjorte Byggesager')
                worksheet = writer.sheets['Modtagne & Afgjorte Byggesager']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
            output.seek(0)

            st.download_button(
                label="Eksporter Modtagne & Afgjorte byggesager til Excel",
                data=output,
                file_name="byggesager_modtagne_afgjorte_alle_år.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )
        else:
            chart_df = df[df["År"] == selected_year].dropna(subset=["MånedNavn", "Type", "Antal"])
            chart_df = chart_df.groupby(["Måned", "MånedNavn", "Type"], as_index=False)["Antal"].sum()
            month_order = get_month_order()
            chart_df["MånedNavn"] = pd.Categorical(chart_df["MånedNavn"], categories=month_order, ordered=True)

            total_modtagne = int(chart_df[chart_df["Type"] == "Modtagede"]["Antal"].sum())
            total_afgjorte = int(chart_df[chart_df["Type"] == "Afgjorte"]["Antal"].sum())

            col1, col2 = st.columns([1, 1])
            with col1:
                ui.metric_card(
                    title="Samlet antal Modtagne byggesager",
                    content=total_modtagne,
                    description=f"Modtagne byggesager i {selected_year}."
                )
            with col2:
                ui.metric_card(
                    title="Samlet antal Afgjorte byggesager",
                    content=total_afgjorte,
                    description=f"Afgjorte byggesager i {selected_year}."
                )

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
            st.altair_chart(chart, width="stretch")

            export_df = chart_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
            export_df = export_df[["Periode", "Type", "Antal"]]
            export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Modtagne & Afgjorte Byggesager')
                worksheet = writer.sheets['Modtagne & Afgjorte Byggesager']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
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
        modtagne_df = df[(df["Type"] == "Modtagede")].dropna(subset=["MånedNavn", "Antal"])

        modtagne_df = modtagne_df.groupby(["År", "Måned", "MånedNavn"], as_index=False)["Antal"].sum()
        month_order = get_month_order()
        modtagne_df["MånedNavn"] = pd.Categorical(modtagne_df["MånedNavn"], categories=month_order, ordered=True)

        total_modtagne = int(modtagne_df["Antal"].sum())
        col1, = st.columns([1])
        with col1:
            ui.metric_card(
                title="Samlet antal Modtagne byggesager",
                content=total_modtagne,
                description=f"Modtagne byggesager i {selected_year}."
            )

        st.header(f"Antal Modtagne Byggesager - {selected_year}", divider="gray")

        chart = sag_count_bar_chart_with_lines(modtagne_df, selected_year)
        st.altair_chart(chart.properties(width=700, height=400), width="stretch")

        export_df = modtagne_df.copy()
        export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
        export_df = export_df[["Periode", "Antal"]]
        export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Modtagne')
            worksheet = writer.sheets['Modtagne']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
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
        afgjorte_df = df[(df["Type"] == "Afgjorte")].dropna(subset=["MånedNavn", "Antal"])
        afgjorte_df = afgjorte_df.groupby(["År", "Måned", "MånedNavn"], as_index=False)["Antal"].sum()
        month_order = get_month_order()
        afgjorte_df["MånedNavn"] = pd.Categorical(afgjorte_df["MånedNavn"], categories=month_order, ordered=True)

        total_afgjorte = int(afgjorte_df["Antal"].sum())
        col1, = st.columns([1])
        with col1:
            ui.metric_card(
                title="Samlet antal Afgjorte byggesager",
                content=total_afgjorte,
                description=f"Afgjorte byggesager i {selected_year}."
            )

        st.header(f"Antal Afgjorte Byggesager - {selected_year}", divider="gray")

        chart = sag_count_bar_chart_with_lines(afgjorte_df, selected_year)
        st.altair_chart(chart.properties(width=700, height=400), width="stretch")

        export_df = afgjorte_df.copy()
        export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
        export_df = export_df[["Periode", "Antal"]]
        export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Afgjorte')
            worksheet = writer.sheets['Afgjorte']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
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
        month_order = get_month_order()
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
        st.altair_chart(chart, width="stretch")

        export_df = afgjorte_type_df.copy()
        export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
        export_df = export_df[["Periode", "Beslutningstype", "Antal"]]
        export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Afgørelsestype')
            worksheet = writer.sheets['Afgørelsestype']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
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
        month_order = get_month_order()
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
        st.altair_chart(chart, width="stretch")

        export_df = modtagede_type_df.copy()
        export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
        export_df = export_df[["Periode", "Gruppering", "Antal"]]
        export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Type')
            worksheet = writer.sheets['Type']
            for i, col in enumerate(export_df.columns):
                max_len = max(
                    export_df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
        output.seek(0)

        st.download_button(
            label="Eksporter Modtagede Byggesager Typer til Excel",
            data=output,
            file_name=f"byggesager_type_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            icon=":material/add_chart:"
        )
