import pandas as pd
import calendar
from utils.database_connection import get_byggesager_db

db_client = get_byggesager_db()


def fetch_kategori_data():
    query = """
    SELECT "Fra Dato", "Kategori", "Sagsbehandlingstid", "Servicemål i procent"
    FROM "bom_data"
    """
    try:
        result = db_client.execute_sql(query)
        if result is not None:
            return pd.DataFrame(result, columns=['Fra Dato', 'Kategori', 'Sagsbehandlingstid', 'Servicemål i procent'])
        else:
            raise ValueError("Failed to fetch data from the database.")
    finally:
        db_client.close_connection()


def process_kategori_data(data):
    data['Fra Dato'] = pd.to_datetime(data['Fra Dato'], format='%d-%m-%Y')
    data['Sagsbehandlingstid'] = data['Sagsbehandlingstid'].astype(str).str.replace(',', '.').astype(float)
    data['Servicemål i procent'] = data['Servicemål i procent'].astype(str).str.replace(',', '.').astype(float)

    data['Year'] = data['Fra Dato'].dt.year
    data['Month'] = data['Fra Dato'].dt.month
    data['Måned'] = data['Month'].apply(lambda x: calendar.month_abbr[x])

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
