import os
from time import time
import argparse

import pandas as pd
from sqlalchemy import create_engine


def change_type_to_datetime(df):
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)


CSV_NAME = 'yellow_tripdata_2021-01.csv'

def download_file(url):
    os.system(f"wget {url} -o {CSV_NAME}")

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    # url = params.url

    # download_file(url)

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    df = pd.read_csv(CSV_NAME, nrows=100)
    change_type_to_datetime(df)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    df_iter = pd.read_csv(CSV_NAME, iterator=True, chunksize=100000)
    try:
        while True:

            t_start = time()

            df = next(df_iter)
            change_type_to_datetime(df)

            df.to_sql(name=table_name, con=engine, if_exists="append")

            t_end = time()

            print(f"inserted another chunk,... took {(t_end - t_start)} second")
    except StopIteration:
        print("Done!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog = 'Ingest Data',
        description = 'Ingest CSV data to Postgres'
    )

    parser.add_argument("--user", help="username for postgres")
    parser.add_argument("--password", help="password for postgres")
    parser.add_argument("--host", help="host for postgres")
    parser.add_argument("--port", help="port for postgres")
    parser.add_argument("--db", help="database name for postgres")
    parser.add_argument(
        "--table_name",
        help="the name of the table where we will write the results to"
    )
    # parser.add_argument("url", help="url of the csv file")

    args = parser.parse_args()
    main(args)