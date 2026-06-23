import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from utils.database_connection import get_byggesager_db
from utils.byggesager_data import get_month_map, get_month_order
import streamlit_shadcn_ui as ui

db_client = get_byggesager_db()

BYGGESAGER_TABS = [
    {
        "value": "Antal Modtagne & Afgjorte byggesager",
        "label": "Modtagne & Afgjorte",
        "pill": "Samlet",
        "icon": (
            "https://cdn.jsdelivr.net/npm/"
            "bootstrap-icons@1.11.3/icons/building.svg"
        ),
        "container_key": "byggesager_combined_tab",
    },
    {
        "value": "Antal Modtagne Byggesager",
        "label": "Modtagne",
        "pill": "Byggesager",
        "icon": (
            "https://cdn.jsdelivr.net/npm/"
            "bootstrap-icons@1.11.3/icons/building-add.svg"
        ),
        "container_key": "byggesager_received_tab",
    },
    {
        "value": "Antal Afgjorte Byggesager",
        "label": "Afgjorte",
        "pill": "Byggesager",
        "icon": (
            "https://cdn.jsdelivr.net/npm/"
            "bootstrap-icons@1.11.3/icons/building-fill-check.svg"
        ),
        "container_key": "byggesager_decided_tab",
    },
    {
        "value": "Antal Modtagede Byggesager opdelt efter Type",
        "label": "Byggesagstype",
        "pill": "Modtagne",
        "icon": (
            "https://cdn.jsdelivr.net/npm/"
            "bootstrap-icons@1.11.3/icons/buildings-fill.svg"
        ),
        "container_key": "byggesager_received_type_tab",
    },
    {
        "value": (
            "Antal Afgjorte Byggesager "
            "opdelt efter Afgørelsestype"
        ),
        "label": "Afgørelsestype",
        "pill": "Afgjorte",
        "icon": (
            "https://cdn.jsdelivr.net/npm/"
            "bootstrap-icons@1.11.3/icons/buildings.svg"
        ),
        "container_key": "byggesager_decision_type_tab",
    },
]


def render_byggesager_tabs() -> str:
    """Render the five handmade Byggesager tabs."""

    state_key = "byggesager_active_tab"

    if state_key not in st.session_state:
        st.session_state[state_key] = BYGGESAGER_TABS[0]["value"]

    selected_tab = st.session_state[state_key]

    tab_specific_css = []

    for tab in BYGGESAGER_TABS:
        tab_specific_css.append(
            f"""
.st-key-{tab["container_key"]} button p::before {{
    background-image: url("{tab["icon"]}");
}}

.st-key-{tab["container_key"]} button p::after {{
    content: "{tab["pill"]}";
}}
"""
        )

    st.markdown(
        f"""
<style>
/* Wrapper around all five tabs */
.st-key-byggesager_tabs {{
    width: 100%;
    margin-bottom: 1.5rem;
}}

/* Five equal-width columns */
.st-key-byggesager_tabs
[data-testid="stHorizontalBlock"] {{
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 1rem !important;
    width: 100%;
}}

/* Remove Streamlit column width restrictions */
.st-key-byggesager_tabs
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"] {{
    width: 100% !important;
    min-width: 0 !important;
    flex: none !important;
}}

/* Tab containers */
.st-key-byggesager_combined_tab,
.st-key-byggesager_received_tab,
.st-key-byggesager_decided_tab,
.st-key-byggesager_received_type_tab,
.st-key-byggesager_decision_type_tab {{
    width: 100%;
}}

/* Full-width button wrappers */
.st-key-byggesager_combined_tab [data-testid="stButton"],
.st-key-byggesager_received_tab [data-testid="stButton"],
.st-key-byggesager_decided_tab [data-testid="stButton"],
.st-key-byggesager_received_type_tab [data-testid="stButton"],
.st-key-byggesager_decision_type_tab [data-testid="stButton"] {{
    width: 100%;
    margin: 0;
}}

/* Shared tab appearance */
.st-key-byggesager_combined_tab button,
.st-key-byggesager_received_tab button,
.st-key-byggesager_decided_tab button,
.st-key-byggesager_received_type_tab button,
.st-key-byggesager_decision_type_tab button {{
    width: 100% !important;
    min-height: 118px;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 12px 8px;
    margin: 0;

    background-color: transparent !important;
    color: #34343c !important;

    border: none !important;
    border-bottom: 2px solid #dddddd !important;
    border-radius: 0 !important;

    box-shadow: none !important;
}}

/* Remove default focus styling */
.st-key-byggesager_combined_tab button:focus,
.st-key-byggesager_received_tab button:focus,
.st-key-byggesager_decided_tab button:focus,
.st-key-byggesager_received_type_tab button:focus,
.st-key-byggesager_decision_type_tab button:focus,
.st-key-byggesager_combined_tab button:active,
.st-key-byggesager_received_tab button:active,
.st-key-byggesager_decided_tab button:active,
.st-key-byggesager_received_type_tab button:active,
.st-key-byggesager_decision_type_tab button:active {{
    box-shadow: none !important;
    outline: none !important;
}}

/* Hover appearance */
.st-key-byggesager_combined_tab button:hover,
.st-key-byggesager_received_tab button:hover,
.st-key-byggesager_decided_tab button:hover,
.st-key-byggesager_received_type_tab button:hover,
.st-key-byggesager_decision_type_tab button:hover {{
    background-color: #fafafa !important;
    color: #34343c !important;
}}

/* Icon, title and pill layout */
.st-key-byggesager_combined_tab button p,
.st-key-byggesager_received_tab button p,
.st-key-byggesager_decided_tab button p,
.st-key-byggesager_received_type_tab button p,
.st-key-byggesager_decision_type_tab button p {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;

    width: 100%;
    margin: 0;

    color: #34343c !important;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.25;
    text-align: center;
    white-space: normal;
}}

/* Bootstrap icon */
.st-key-byggesager_combined_tab button p::before,
.st-key-byggesager_received_tab button p::before,
.st-key-byggesager_decided_tab button p::before,
.st-key-byggesager_received_type_tab button p::before,
.st-key-byggesager_decision_type_tab button p::before {{
    content: "";

    display: block;
    width: 21px;
    height: 21px;
    flex: 0 0 21px;

    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}}

/* Grey pill */
.st-key-byggesager_combined_tab button p::after,
.st-key-byggesager_received_tab button p::after,
.st-key-byggesager_decided_tab button p::after,
.st-key-byggesager_received_type_tab button p::after,
.st-key-byggesager_decision_type_tab button p::after {{
    display: inline-block;
    padding: 3px 9px;

    background-color: #f1f1f1;
    border: 1px solid #d1d1d1;
    border-radius: 999px;

    color: #55555d;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.2;
    white-space: nowrap;
}}

{"".join(tab_specific_css)}

/* Three columns on medium-width screens */
@media (max-width: 1200px) {{
    .st-key-byggesager_tabs
    [data-testid="stHorizontalBlock"] {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
}}

/* One column on small screens */
@media (max-width: 700px) {{
    .st-key-byggesager_tabs
    [data-testid="stHorizontalBlock"] {{
        grid-template-columns: 1fr;
        gap: 0.5rem !important;
    }}

    .st-key-byggesager_combined_tab button,
    .st-key-byggesager_received_tab button,
    .st-key-byggesager_decided_tab button,
    .st-key-byggesager_received_type_tab button,
    .st-key-byggesager_decision_type_tab button {{
        min-height: 80px;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )

    active_container_key = next(
        tab["container_key"]
        for tab in BYGGESAGER_TABS
        if tab["value"] == selected_tab
    )

    # Dark underline beneath the selected tab.
    st.markdown(
        f"""
<style>
.st-key-{active_container_key} button {{
    border-bottom-color: #2f2f2f !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )

    def select_byggesager_tab(tab_value: str) -> None:
        st.session_state[state_key] = tab_value

    with st.container(key="byggesager_tabs"):
        tab_columns = st.columns(
            len(BYGGESAGER_TABS),
            gap="small",
        )

        for column, tab in zip(tab_columns, BYGGESAGER_TABS):
            with column:
                with st.container(key=tab["container_key"]):
                    st.button(
                        tab["label"],
                        key=f'{tab["container_key"]}_button',
                        use_container_width=True,
                        on_click=select_byggesager_tab,
                        args=(tab["value"],),
                    )

    return st.session_state[state_key]


def get_byggesager_overview():
    content_tabs = render_byggesager_tabs()

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
        month_map = get_month_map()
        df["MånedNavn"] = df["Måned"].map(month_map)
        df["Antal"] = pd.to_numeric(df["Antal"], errors="coerce")

        available_years = sorted(df["År"].unique())
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
                    x=alt.X('År:N', title='År', sort=available_years[:-1]),
                    y=alt.Y('Antal:Q', title='Antal byggesager'),
                    xOffset=alt.XOffset('Type:N', title='Type'),
                    color=alt.Color('Type:N', title='Type'),
                    tooltip=[
                        alt.Tooltip('År:N', title='År'),
                        alt.Tooltip('Type:N', title='Type'),
                        alt.Tooltip('Antal:Q', title='Antal')
                    ]
                ).properties(width=700, height=400)
                st.altair_chart(chart, use_container_width=True)

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
                st.altair_chart(chart, use_container_width=True)

                export_df = chart_df.copy()
                export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
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
            modtagne_df = df[(df["År"] == selected_year) & (df["Type"] == "Modtagede")].dropna(subset=["MånedNavn", "Antal"])
            modtagne_df = modtagne_df.groupby(["Måned", "MånedNavn"], as_index=False)["Antal"].sum()
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
            afgjorte_df = df[(df["År"] == selected_year) & (df["Type"] == "Afgjorte")].dropna(subset=["MånedNavn", "Antal"])
            afgjorte_df = afgjorte_df.groupby(["Måned", "MånedNavn"], as_index=False)["Antal"].sum()
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
            st.altair_chart(chart, use_container_width=True)

            export_df = afgjorte_type_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
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
            st.altair_chart(chart, use_container_width=True)

            export_df = modtagede_type_df.copy()
            export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
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

    except Exception as e:
        st.error(f'Fejl ved hentning af byggesagsdata: {e}')
    finally:
        db_client.close_connection()
