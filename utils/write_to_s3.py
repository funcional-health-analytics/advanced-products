import boto3
import pandas as pd
import io
import awswrangler as wr
import os



def write_xlsx_to_s3(df, bucket, path, sheet_name='sheet'):
    
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name)
        data = output.getvalue()
    
    east_session = boto3.Session( region_name='us-east-1',
                                  aws_access_key_id='ASIA6QLRFGTFSP3ALLIQ',
                                  aws_secret_access_key='2gLgfP4Jw52lO7JohlIcA132DSSNh6X4QwjDJmR6',
                                  aws_session_token= 'IQoJb3JpZ2luX2VjEBoaCXVzLWVhc3QtMSJHMEUCIQD7JQ/EO2/D4O2ThiORXm0u2o/Fh8Pk0YMOWpaEMPmRzwIgUkMqJ3czr24AJwcP3yk5es0lNGNaJ1lZDJji4wuJEtUqrgMIYxADGgw5OTcyMDY2MDI5NTUiDFdHSCzs1mGXalWAbyqLA2eD4eQP3u8LZGgLmQ6BZy1cXTfuSppfvPV9sPB01wOd0csbEJS1iz9tmpqVaYcLtfKRRU4Do3d7lppaupnc9nCnAP2bXgou2hQ5KWLMv5/H37bSiN40BpwBoW8eBpd+r8Sr+CNIMIeREs7UJbi1KPfcOVzWK3eCZtKrh2sdG9aJvxvQCpOVU2ghkW2l3mM593G+iz4WyXiiY3vHy7rATsXbhU2WbsEHlx0cK9UUltR2fClKRJxaSeO5sSmkGFbDP5np0wia1CJz2a/aqfjBMvelDnohMKnQflw75k3t9sqwSGaUUFdSuxeALz/uBNjzsyo/uqdrHlJGVw5etukJ8GeeV/usQwttz2A/g2XRtgYECCtcLqNiJcCtyDgsUlculeXd6m1eAAFEA0H6tciecj/lZ6gKrpjc4mvOQW+AiB+RGvADQFWglkprJaKdCNcYHhp77hibwweBu4gWIt0g1Za4Dj7g81U8DR8SrygtA8w9oMA1P8VwGEuJfx4SWwranHU69+X7T0DutklyMKuat50GOqYBZGOGGocKlC6DMzdO2aoMDgKEcDmz/5XrKoCLxJmJJxfH6Y4oYHDbyvsHm5siSb2UDyzkcv4H5mspynuSZ81TkxmwH7RsGp3OnksCSpxRqx244go5v8S+2xc0vX5Q70WRctvNwqdNQWyEk1wBld1Z5ecVinMFSAhMvYqtwFUnt6JcM9uy7TsxhS4/8bEzI/d+6yZjp2jznhEyjfsD6OlADQhgJInMow==')
    
    s3 = east_session.resource("s3")

    #s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=path, Body=data)


def write_csv_to_s3(df, bucket, path):
    df.to_csv(f"s3://{bucket}/{path}", index=False)


def write_parquet_to_s3(df, bucket, path):
    wr.s3.to_parquet(df=df,
                     path=f"s3://{bucket}/{path}",
                     compression='gzip')


def save_model_to_s3(model, bucket, path):
    model.save(f"s3://{bucket}/{path}")

