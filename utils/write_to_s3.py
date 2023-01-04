import boto3
import pandas as pd
import io
from io import StringIO
import awswrangler as wr
import os
import s3fs


def write_xlsx_to_s3(df, bucket, path, sheet_name='sheet'):
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name)
        data = output.getvalue()
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=path, Body=data)


def write_csv_to_s3(df, bucket, path):
    df.to_csv(f"s3://{bucket}/{path}", index=False)


def write_parquet_to_s3(df, bucket, path):
    wr.s3.to_parquet(df=df,
                     path=f"s3://{bucket}/{path}",
                     compression='gzip')


def save_model_to_s3(model, bucket, path):
    model.save(f"s3://{bucket}/{path}")

