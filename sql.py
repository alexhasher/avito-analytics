from config import host, user, password, db_name
import sqlalchemy
import pandas as pd
from datetime import datetime


def top10_offer(dbase_name):
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = f"SELECT * FROM `{dbase_name}`"
    df = pd.read_sql_query(sql, engine)
    return df.nlargest(10, ['views_all'])

def concurents(dbase_name):
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = f"SELECT * FROM `{dbase_name}`"
    df = pd.read_sql_query(sql, engine)
    insiders = {}
    list_insiders1 = []
    list_insiders2 = []
    list_insiders3 = []
    for i in df.category.unique():
        list_insiders1.append(i)
        list_insiders2.append(int(df.loc[df['category'] == i, 'views_all'].sum()))
        list_insiders3.append(len(df.loc[df['category'] == i]))
    insiders['category'] = list_insiders1
    insiders['views_all'] = list_insiders2
    insiders['count_offers'] = list_insiders3
    df = pd.DataFrame(insiders)
    return df

def concurents_today(dbase_name):
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = f"SELECT * FROM `{dbase_name}`"
    df = pd.read_sql_query(sql, engine)
    insiders = {}
    list_insiders1 = []
    list_insiders2 = []
    list_insiders3 = []
    for i in df.category.unique():
        list_insiders1.append(i)
        list_insiders2.append(int(df.loc[df['category'] == i, 'views_today'].sum()))
        list_insiders3.append(len(df.loc[(df['category'] == i) & (df['publish_date'] == datetime.now().date())]))
    insiders['category'] = list_insiders1
    insiders['views_today'] = list_insiders2
    insiders['count_offers'] = list_insiders3
    df = pd.DataFrame(insiders)
    return df

def top10_offer_today(dbase_name):
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = f"SELECT * FROM `{dbase_name}`"
    df = pd.read_sql_query(sql, engine)
    return df.nlargest(10, ['views_today'])

def all_offer(dbase_name):
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = f"SELECT * FROM `{dbase_name}`"
    df = pd.read_sql_query(sql, engine)
    return df