import pandas as pd

from datetime import datetime, date
from sqlalchemy import extract, func

from models import ByggesagByg, ByggesagSag, Byggesagskode, Byggesagsgruppe, Beslutningstype
from utils.database import DatabaseClient
from utils.config import BYGGESAGER_POSTGRES_DB_DATABASE, BYGGESAGER_POSTGRES_DB_USER, \
    BYGGESAGER_POSTGRES_DB_PASS, BYGGESAGER_POSTGRES_DB_HOST, BYGGESAGER_POSTGRES_DB_PORT


db_client = DatabaseClient(
    database=BYGGESAGER_POSTGRES_DB_DATABASE,
    username=BYGGESAGER_POSTGRES_DB_USER,
    password=BYGGESAGER_POSTGRES_DB_PASS,
    host=BYGGESAGER_POSTGRES_DB_HOST,
    port=BYGGESAGER_POSTGRES_DB_PORT
)


def get_modtagne_byggesager(grupper: list[str], start_year: int, end_year: int = None) -> pd.DataFrame:
    start_date = date(start_year, 1, 1)
    end_date = None
    if end_year:
        if end_year < datetime.now().year:
            end_date = date(end_year + 1, 1, 1)

    if not end_date:
        end_date = date.today().replace(day=1)

    with db_client.get_sqlalchemy_session() as session:
        results = []
        for source_model in [ByggesagByg, ByggesagSag]:
            res = session.query(
                extract('year', source_model.received_date).label('År'),
                extract('month', source_model.received_date).label('Måned'),
                Byggesagsgruppe.name.label('Gruppering'),
                Byggesagskode.name.label('AnsøgningsType'),
                func.count(source_model.id).label('Antal')) \
                .select_from(
                    source_model
            ).join(
                Byggesagskode, source_model.byggesagskode_id == Byggesagskode.id
            ).join(
                Byggesagsgruppe, Byggesagsgruppe.id == Byggesagskode.byggesagsgruppe_id
            ).filter(
                source_model.received_date >= start_date,
                source_model.received_date <= end_date,
                Byggesagsgruppe.name.in_(grupper)
            ).group_by(
                extract('year', source_model.received_date),
                extract('month', source_model.received_date),
                Byggesagsgruppe.name,
                Byggesagskode.name
            ).all()
            results.append(res)
    return pd.DataFrame(results[0] + results[1], columns=[
        'År', 'Måned', 'Gruppering', 'Ansøgningstype', 'Antal'
    ])


def get_afgjorte_byggesager(grupper: list[str], start_year: int, end_year: int = None) -> pd.DataFrame:
    start_date = date(start_year, 1, 1)
    end_date = None
    if end_year:
        if end_year < datetime.now().year:
            end_date = date(end_year + 1, 1, 1)

    if not end_date:
        end_date = date.today().replace(day=1)

    with db_client.get_sqlalchemy_session() as session:
        results = []
        for source_model in [ByggesagByg, ByggesagSag]:
            res = session.query(
                extract('year', source_model.byggetilladelse_date).label('År'),
                extract('month', source_model.byggetilladelse_date).label('Måned'),
                Byggesagsgruppe.name.label('Gruppering'),
                Beslutningstype.name.label('Beslutningstype'),
                func.count(source_model.id).label('Antal')) \
                .select_from(source_model) \
                .join(Byggesagskode, source_model.byggesagskode_id == Byggesagskode.id) \
                .join(Byggesagsgruppe, Byggesagsgruppe.id == Byggesagskode.byggesagsgruppe_id) \
                .join(Beslutningstype, source_model.beslutningstype_id == Beslutningstype.id) \
                .filter(
                    source_model.byggetilladelse_date >= start_date,
                    source_model.byggetilladelse_date < end_date,
                    Byggesagsgruppe.name.in_(grupper)
            ).group_by(
                    extract('year', source_model.byggetilladelse_date),
                    extract('month', source_model.byggetilladelse_date),
                    Byggesagskode.name,
                    Byggesagsgruppe.name,
                    Beslutningstype.name
            ).all()
            results.append(res)
    return pd.DataFrame(results[0] + results[1], columns=[
        'År', 'Måned', 'Gruppering', 'Beslutningstype', 'Antal'
    ])
