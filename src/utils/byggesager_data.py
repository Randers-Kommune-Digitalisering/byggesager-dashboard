import pandas as pd
import calendar
from utils.database_connection import get_byggesager_db

db_client = get_byggesager_db()


def fetch_monthly_data():
    query = """
    SELECT "Fra Dato", "Kategori", "Sagsbehandlingstid", "Servicemål i procent"
    FROM "bom_data_monthly"
    """
    try:
        result = db_client.execute_sql(query)
        if result is not None:
            return pd.DataFrame(result, columns=['Fra Dato', 'Kategori', 'Sagsbehandlingstid', 'Servicemål i procent'])
        else:
            raise ValueError("Failed to fetch Monthly data from the database.")
    finally:
        db_client.close_connection()


def fetch_glidende_gennemsnit_data():
    query = """
    SELECT "Fra Dato", "Til Dato", "Kategori", "Sagsbehandlingstid", "Servicemål i procent"
    FROM "bom_data_glidende"
    """
    db_client = get_byggesager_db()
    try:
        result = db_client.execute_sql(query)
        if result is not None:
            return pd.DataFrame(
                result,
                columns=["Fra Dato", "Til Dato", "Kategori", "Sagsbehandlingstid", "Servicemål i procent"],
            )
        raise ValueError("Failed to fetch Glidende Gennemsnit data from the database.")
    finally:
        db_client.close_connection()


def process_monthly_data(data):
    data['Fra Dato'] = pd.to_datetime(data['Fra Dato'], format='%d-%m-%Y')
    data['Sagsbehandlingstid'] = data['Sagsbehandlingstid'].astype(str).str.replace(',', '.').astype(float)
    data['Servicemål i procent'] = data['Servicemål i procent'].astype(str).str.replace(',', '.').astype(float)

    data['Year'] = data['Fra Dato'].dt.year
    data['Month'] = data['Fra Dato'].dt.month
    data['Måned'] = data['Month'].apply(lambda x: calendar.month_abbr[x])

    return data


def process_glidende_gennemsnit_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Glidende gennemsnit vises for måneden, der slutter ved 'Til Dato'.
    Rækker uden gyldige værdier for begge mål vises ikke.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    data = data.copy()
    data["Fra Dato"] = pd.to_datetime(data["Fra Dato"], format="%d-%m-%Y")
    data["Til Dato"] = pd.to_datetime(data["Til Dato"], format="%d-%m-%Y")

    data["Sagsbehandlingstid"] = pd.to_numeric(
        data["Sagsbehandlingstid"].astype(str).str.replace(",", "."),
        errors="coerce",
    )
    data["Servicemål i procent"] = pd.to_numeric(
        data["Servicemål i procent"].astype(str).str.replace(",", "."),
        errors="coerce",
    )

    valid_values = (
        data["Sagsbehandlingstid"].gt(0)
        & data["Servicemål i procent"].gt(0)
    )
    data = data.loc[valid_values].copy()

    # 'Til Dato' is the end of the monthly period represented by the row.
    data["Visningsdato"] = data["Til Dato"] - pd.DateOffset(months=1)

    data["Year"] = data["Visningsdato"].dt.year
    data["Month"] = data["Visningsdato"].dt.month
    data["Måned"] = data["Month"].apply(lambda x: calendar.month_abbr[x])

    return data


def get_categories():
    return [
        "Gennemsnit/Sum",
        "Simple Konstruktioner (byg)",
        "Enfamilieshuse (byg)",
        "Industri og lagerbygninger (byg)",
        "Etagebyggeri, Erhverv (byg)",
        "Etagebyggeri, Boliger (byg)"
    ]


def get_month_map():
    return {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
    }


def get_month_order():
    return ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
