import altair as alt
import pandas as pd
import streamlit_antd_components as sac
import streamlit as st
import streamlit_shadcn_ui as ui
from io import BytesIO

from utils.byggesager_data import get_month_map, get_month_order
from utils.chart import sag_count_bar_chart_with_lines
from data import get_modtagne_byggesager, get_afgjorte_byggesager


def get_landzonesager_overview():
    content_tabs = sac.tabs([
        sac.TabsItem('Antal Modtagne & Afgjorte landzonesager', tag='Modtagne & Afgjorte', icon='bi bi-building'),
        sac.TabsItem('Antal Modtagne Landzonesager', tag='Modtagne Landzonesager', icon='bi bi-building-add'),
        sac.TabsItem('Antal Afgjorte Landzonesager', tag='Afgjorte Landzonesager', icon='bi bi-building-fill-check'),
        sac.TabsItem('Antal Modtagne landzonesager opdelt efter Ansøgningstype', tag='Ansøgningstype', icon='bi bi-buildings-fill'),
        sac.TabsItem('Antal Afgjorte Landzonesager opdelt efter Type', tag='Type', icon='bi bi-buildings'),
    ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'landzonesager_data' not in st.session_state:
            with st.spinner('Indlæser landzonesagsdata...'):
                df_modtagede = get_modtagne_byggesager(
                    grupper=["Landzone"],
                    start_year=2020
                )
                df_modtagede["Type"] = "Modtagede"

                df_afgjorte = get_afgjorte_byggesager(
                    grupper=["Landzone"],
                    start_year=2020
                )
                df_afgjorte["Type"] = "Afgjorte"

                df = pd.concat([df_modtagede, df_afgjorte], ignore_index=True)
                st.session_state.landzonesager_data = df

        df = st.session_state.landzonesager_data.copy()

        month_map = get_month_map()
        df["MånedNavn"] = df["Måned"].map(month_map)
        df["Antal"] = pd.to_numeric(df["Antal"], errors="coerce")

        available_years = sorted(df["År"].unique())[2:]
        if content_tabs == 'Antal Modtagne & Afgjorte landzonesager':
            available_years.append("Alle år")
            selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 2)
        else:
            selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 1)

        if content_tabs == 'Antal Modtagne & Afgjorte landzonesager':
            if selected_year == "Alle år":
                samlet_df = df.dropna(subset=["År", "Type", "Antal"])
                samlet_df = samlet_df.groupby(["År", "Type"], as_index=False)["Antal"].sum()
                total_modtagne = int(samlet_df[samlet_df["Type"] == "Modtagede"]["Antal"].sum())
                total_afgjorte = int(samlet_df[samlet_df["Type"] == "Afgjorte"]["Antal"].sum())

                col1, col2 = st.columns([1, 1])
                with col1:
                    ui.metric_card(
                        title="Samlet antal Modtagne landzonesager",
                        content=total_modtagne,
                        description="Modtagne landzonesager (alle år)."
                    )
                with col2:
                    ui.metric_card(
                        title="Samlet antal Afgjorte landzonesager",
                        content=total_afgjorte,
                        description="Afgjorte landzonesager (alle år)."
                    )

                st.header("Antal modtagne og afgjorte landzonesager - Alle år", divider="gray")
                chart = alt.Chart(samlet_df).mark_bar().encode(
                    x=alt.X("År:N", title="År", sort=available_years[:-1]),
                    y=alt.Y("Antal:Q", title="Antal landzonesager"),
                    xOffset=alt.XOffset("Type:N", title="Type"),
                    color=alt.Color("Type:N", title="Type"),
                    tooltip=[
                        alt.Tooltip("År:N", title="År"),
                        alt.Tooltip("Type:N", title="Type"),
                        alt.Tooltip("Antal:Q", title="Antal")
                    ]
                ).properties(width=700, height=400)
                st.altair_chart(chart, use_container_width=True)

                export_df = samlet_df.copy()
                export_df["Periode"] = export_df["År"].astype(str)
                export_df = export_df[["Periode", "Type", "Antal"]]
                export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Samlet')
                    worksheet = writer.sheets['Samlet']
                for i, col in enumerate(export_df.columns):
                    max_len = max(
                        export_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
                output.seek(0)

                st.download_button(
                    label="Eksporter samlet data til Excel",
                    data=output,
                    file_name="landzonesager_samlet_alle_år.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    icon=":material/add_chart:"
                )
            else:
                samlet_df = df[df["År"] == selected_year].dropna(subset=["MånedNavn", "Type", "Antal"])
                samlet_df = samlet_df.groupby(["Måned", "MånedNavn", "Type"], as_index=False)["Antal"].sum()
                month_order = get_month_order()
                samlet_df["MånedNavn"] = pd.Categorical(samlet_df["MånedNavn"], categories=month_order, ordered=True)

                total_modtagne = int(samlet_df[samlet_df["Type"] == "Modtagede"]["Antal"].sum())
                total_afgjorte = int(samlet_df[samlet_df["Type"] == "Afgjorte"]["Antal"].sum())

                col1, col2 = st.columns([1, 1])
                with col1:
                    ui.metric_card(
                        title="Samlet antal Modtagne landzonesager",
                        content=total_modtagne,
                        description=f"Modtagne landzonesager i {selected_year}."
                    )
                with col2:
                    ui.metric_card(
                        title="Samlet antal Afgjorte landzonesager",
                        content=total_afgjorte,
                        description=f"Afgjorte landzonesager i {selected_year}."
                    )

                st.header(f"Antal modtagne og afgjorte landzonesager - {selected_year}", divider="gray")
                chart = alt.Chart(samlet_df).mark_bar().encode(
                    x=alt.X("MånedNavn:N", title="Måned", sort=month_order),
                    y=alt.Y("Antal:Q", title="Antal landzonesager"),
                    xOffset=alt.XOffset("Type:N", title="Type"),
                    color=alt.Color("Type:N", title="Type"),
                    tooltip=[
                        alt.Tooltip("MånedNavn:N", title="Måned"),
                        alt.Tooltip("Type:N", title="Type"),
                        alt.Tooltip("Antal:Q", title="Antal")
                    ]
                ).properties(width=700, height=400)
                st.altair_chart(chart, use_container_width=True)

                export_df = samlet_df.copy()
                export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + str(selected_year)
                export_df = export_df[["Periode", "Type", "Antal"]]
                export_df["Antal"] = export_df["Antal"].map(lambda x: str(x).replace('.', ','))

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Samlet')
                    worksheet = writer.sheets['Samlet']
                for i, col in enumerate(export_df.columns):
                    max_len = max(
                        export_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
                output.seek(0)

                st.download_button(
                    label="Eksporter samlet data til Excel",
                    data=output,
                    file_name=f"landzonesager_samlet_{selected_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    icon=":material/add_chart:"
                )

        elif content_tabs == 'Antal Modtagne Landzonesager':
            modtagne_df = df[df["Type"] == "Modtagede"].dropna(subset=["MånedNavn", "Antal"])
            modtagne_df = modtagne_df.groupby(["År", "Måned", "MånedNavn"], as_index=False)["Antal"].sum()
            month_order = get_month_order()
            modtagne_df["MånedNavn"] = pd.Categorical(modtagne_df["MånedNavn"], categories=month_order, ordered=True)

            total_modtagne = int(modtagne_df["Antal"].sum())
            col1, = st.columns([1])
            with col1:
                ui.metric_card(
                    title="Samlet antal Modtagne landzonesager",
                    content=total_modtagne,
                    description=f"Modtagne landzonesager i {selected_year}."
                )

            st.header(f"Antal Modtagne Landzonesager - {selected_year}", divider="gray")

            chart = sag_count_bar_chart_with_lines(modtagne_df, selected_year)
            st.altair_chart(chart.properties(width=700, height=400), use_container_width=True)

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
                label="Eksporter modtagne landzonesager til Excel",
                data=output,
                file_name=f"landzonesager_modtagne_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Afgjorte Landzonesager':
            afgjorte_df = df[df["Type"] == "Afgjorte"].dropna(subset=["MånedNavn", "Antal"])
            afgjorte_df = afgjorte_df.groupby(["År", "Måned", "MånedNavn"], as_index=False)["Antal"].sum()
            month_order = get_month_order()
            afgjorte_df["MånedNavn"] = pd.Categorical(afgjorte_df["MånedNavn"], categories=month_order, ordered=True)

            total_afgjorte = int(afgjorte_df["Antal"].sum())
            col1, = st.columns([1])
            with col1:
                ui.metric_card(
                    title="Samlet antal afgjorte landzonesager",
                    content=total_afgjorte,
                    description=f"Afgjorte landzonesager i {selected_year}."
                )

            st.header(f"Antal afgjorte landzonesager - {selected_year}", divider="gray")

            chart = sag_count_bar_chart_with_lines(afgjorte_df, selected_year)
            st.altair_chart(chart.properties(width=700, height=400), use_container_width=True)

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
                label="Eksporter afgjorte landzonesager til Excel",
                data=output,
                file_name=f"landzonesager_afgjorte_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Modtagne landzonesager opdelt efter Ansøgningstype':
            st.write(df.head())
            filtered_df = df[(df["År"] == selected_year) & (df["Type"] == "Modtagede")].dropna(subset=["MånedNavn", "Ansøgningstype", "Antal"])
            grouped_df = filtered_df.groupby(["Måned", "MånedNavn", "Ansøgningstype"], as_index=False)["Antal"].sum()
            month_order = get_month_order()
            grouped_df["MånedNavn"] = pd.Categorical(grouped_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Modtagne landzonesager opdelt efter Ansøgningstype - {selected_year}", divider="gray")
            chart = alt.Chart(grouped_df).mark_bar().encode(
                x=alt.X("MånedNavn:N", title="Måned", sort=month_order),
                y=alt.Y("Antal:Q", title="Antal"),
                color=alt.Color("Ansøgningstype:N", title="Type"),
                tooltip=[
                    alt.Tooltip("MånedNavn:N", title="Måned"),
                    alt.Tooltip("Ansøgningstype:N", title="Type"),
                    alt.Tooltip("Antal:Q", title="Antal")
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = grouped_df.copy()
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
                label="Eksporter typer til Excel",
                data=output,
                file_name=f"landzonesager_type_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

        elif content_tabs == 'Antal Afgjorte Landzonesager opdelt efter Afgørelsestype':
            filtered_df = df[(df["År"] == selected_year) & (df["Type"] == "Afgjorte")].dropna(subset=["MånedNavn", "Beslutningstype", "Antal"])
            grouped_df = filtered_df.groupby(["Måned", "MånedNavn", "Beslutningstype"], as_index=False)["Antal"].sum()
            month_order = get_month_order()
            grouped_df["MånedNavn"] = pd.Categorical(grouped_df["MånedNavn"], categories=month_order, ordered=True)

            st.header(f"Antal Afgjorte Landzonesager opdelt efter Type - {selected_year}", divider="gray")
            chart = alt.Chart(grouped_df).mark_bar().encode(
                x=alt.X("MånedNavn:N", title="Måned", sort=month_order),
                y=alt.Y("Antal:Q", title="Antal"),
                color=alt.Color("Beslutningstype:N", title="Type"),
                tooltip=[
                    alt.Tooltip("MånedNavn:N", title="Måned"),
                    alt.Tooltip("Beslutningstype:N", title="Type"),
                    alt.Tooltip("Antal:Q", title="Antal")
                ]
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

            export_df = grouped_df.copy()
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
                label="Eksporter afgørelsestyper til Excel",
                data=output,
                file_name=f"landzonesager_afgorelsetype_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                icon=":material/add_chart:"
            )

    except Exception as e:
        st.error(f'Fejl ved hentning af landzonesagsdata: {e}')
