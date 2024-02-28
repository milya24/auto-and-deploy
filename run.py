import configparser
import os
from datetime import datetime, timedelta

import pandas as pd
from yahoo_fin.stock_info import get_data

from pgdb import PGDatabase

dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, "config.ini"))

COMPANIES = eval(config["Companies"]["COMPANIES"])
SALES_PATH = config["Files"]["SALES_PATH"]
DATABASE_CREDS = config["Database"]

sales_df = pd.DataFrame()
if os.path.exists(SALES_PATH):
    sales_df = pd.read_csv(SALES_PATH)
    # print(sales_df)
    os.remove(SALES_PATH)

historical_d = {}

for company in COMPANIES:
    historical_d[company] = get_data(
        company,
        start_date=(datetime.today() - timedelta(days=1)).strftime("%m/%d/%Y"),
        end_date=datetime.today().strftime("%m/%d/%Y"),
    ).reset_index()
    # print(historical_d[company])


database = PGDatabase(
    host=DATABASE_CREDS["HOST"],
    database=DATABASE_CREDS["DATABASE"],
    user=DATABASE_CREDS["USER"],
    password=DATABASE_CREDS["PASSWORD"],
)

for i, row in sales_df.iterrows():  # {datetime.strptime(row['dt'], '%m/%d/%Y')
    query = f"insert into sales values ('{datetime.strptime(row['dt'], '%d-%m-%Y')}', '{row['company']}', '{row['transaction_type']}', {row['amount']})"
    database.post(query)
    print(query)

for company, data in historical_d.items():
    for i, row in data.iterrows():
        query = f"insert into stock values ('{row['index']}', '{row['ticker']}', {row['open']}, {row['close']})"
        database.post(query)
