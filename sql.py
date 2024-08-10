from config import host, user, password, db_name
import sqlalchemy
import pandas as pd

def top10_offer():
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = "SELECT * FROM `user_data`"
    df = pd.read_sql_query(sql, engine)
    return df.nlargest(10, ['views_all'])

def concurents():
    engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    sql = "SELECT * FROM `user_data`"
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
