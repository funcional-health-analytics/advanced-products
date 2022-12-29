import pandas as pd 
import numexpr as ne
import awswrangler as wr
import sys
import logging
import json
from datetime import datetime
from datetime import date
import snowflake.connector

sys.path.insert(0, 'src/')
from ds_colombia.clv.clv_churn import df_to_clv, create_transactional_table, create_summary_table
from utils.mba_generator import mba_generator
from utils.clv_clusters_missing_products import clv_cluster_missing_products
from utils.anomaly_detector import anomaly_detector
from utils.recommender_generator import recommender
from utils.data_cleaning import mba_data_cleaning


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.info('Loading the client json file.........\n')
with open('clients/clients.json') as json_file:
    data = json.load(json_file)

logging.info('Connecting SnowFlake.........\n')
conn = snowflake.connector.connect(
                user='DSCIENCE',
                password='9VSLp#JtawhNX@UxIaAwnIH!3kwBgN&3Vwn68$M',
                account='lia24005.us-east-1',
                warehouse='CIENCIA_DE_DADOS',
                database='PBM_INTER',
                schema='EXTRACAO'# ,authenticator="externalbrowser"
                )
 
logging.info('Creating a cursor object..........\n')
cur = conn.cursor()

logging.info('Creating a sql query..........\n')
df_sql = f"""
              select product_id, product_name, product_group, sale_date, sale_unity,sale_order_id,
                     sale_total_price,cod_dim_customer,store_name,product_atclevel4_description,
                     customer_type,customer_group,customer_category,customer_salary,
                     customer_city, customer_gender, customer_age, customer_family,
                     product_brand, product_class, product_presentation, product_sub_family, product_family
              from "PBM_INTER"."TRUSTED_COMFANDI"."T_COMFANDI_SALE_TABLEAU"
              where year(SALE_DATE) > 2020 and sale_order_id is not null
          """

logging.info('Executing the sql query..........\n')
cur.execute(df_sql)

logging.info('Fetch the result set from the cursor and deliver it as the Pandas DataFrame..........\n')
df = cur.fetch_pandas_all()
df.columns = df.columns.str.lower()

# Local file to test 
#df = pd.read_parquet('data_test202211.parquet', engine='pyarrow') 
#df = pd.read_parquet('comfandi.parquet')

report_date = str(datetime.now())[:10]
bucket = 'fnc-data-science'
products_path = f"test-colombia/products"
model_path = f"test-colombia/models"
view_path = data['comfandi']['view_path']
client_columns = data['comfandi']['extract_columns']

columns = [client_columns['product_granularity'],
           client_columns['product_name'],
           client_columns['product_group'],
           client_columns['date_column'],
           client_columns['quantity_column'],
           client_columns['order_column'],
           client_columns['value_column'],
           client_columns['customer_column'],
           client_columns['store_granularity'],
           client_columns['anomaly_product_granularity'],
           client_columns['customer_type'],
           client_columns['customer_group'],
           client_columns['customer_category'],
           client_columns['customer_salary'],
           client_columns['customer_city'],
           client_columns['customer_gender'],
           client_columns['customer_age'],
          client_columns['customer_family'],
          client_columns['product_brand'],
          client_columns['product_class'],
          client_columns['product_presentation'],
          client_columns['product_sub_family'],
          client_columns['product_family']]

#logging.info("Reading files. Dont't mind the logging overload")
#df = wr.s3.read_parquet(view_path, columns=columns)

logging.info("\nLet's run the MBA stuff")
allowed_product_types = list(
    pd.read_csv('clients/comfandi/comfandi_product_categories.csv')['Allowed Categories'].values)

df = df[df[client_columns['product_granularity']].isin(allowed_product_types)]


logging.info('Starting with the MBA function......\n')

logging.info('The dataframe shape is\n')
logging.info('Rows- {}'.format(df.shape[0]))
logging.info('Cols- {}'.format(df.shape[1]))
mba_generator(df,
              bucket,
              products_path,
              report_date,
              client_columns['product_granularity'],
              client_columns['product_name'],
              client_columns['product_group'],
              client_columns['date_column'],
              client_columns['quantity_column'],
              client_columns['order_column'],
              client_columns['value_column'],
              n_products=300,
              n_rules = 500,
              min_support=0.00005,
              max_len=2,
              allowed_product_types=allowed_product_types,
              customer='comfandi')

logging.info("\nMBA finished without problems\n")

logging.info("Now it's the CLV and missing products turn")
end_date = date.today().strftime("%Y-%m-%d")
clv_cluster_missing_products(df,
                              bucket,
                              products_path,
                              report_date,
                              client_columns['product_granularity'],
                              client_columns['product_name'],
                              client_columns['date_column'],
                              client_columns['quantity_column'],
                              client_columns['order_column'],
                              client_columns['customer_column'],
                              client_columns['store_granularity'],
                              client_columns['value_column'],
                              end_date,
                              period_months=12,
                              customer='comfandi') 

logging.info("\n Clv  missing products \n")

logging.info("Anomalies time!")
anomaly_detector(df,
                  bucket,
                  products_path,
                  report_date,
                  client_columns['anomaly_product_granularity'],
                  client_columns['product_name'],
                  client_columns['date_column'],
                  client_columns['quantity_column'],
                  client_columns['order_column'],
                  client_columns['customer_column'],
                  client_columns['store_granularity'],
                  stddev=2,
                  customer='comfandi')


logging.info("Finally, recommendations to our special users")
#ne.set_num_threads(ne.detect_number_of_threads())
sales_columns = [client_columns['product_granularity'],
                  client_columns['customer_column']]

customers_columns = [client_columns['customer_column'],
                      client_columns['customer_type'],
                      client_columns['customer_group'],
                      client_columns['customer_category'],
                      client_columns['customer_salary'],
                      client_columns['customer_city'],
                      client_columns['customer_gender'],
                      client_columns['customer_age'],
                      client_columns['customer_family']]

products_columns = [client_columns['product_granularity'],
                     client_columns['product_brand'],
                     client_columns['product_class'],
                     client_columns['product_presentation'],
                     client_columns['product_sub_family'],
                     client_columns['product_family']]

recommender(df,
             bucket,
             products_path,
             model_path,
             report_date,
             sales_columns,
             customers_columns,
             products_columns,
             customer='comfandi',
             n_recommendations=10,
             customer_column=client_columns['customer_column'],
             product_granularity=client_columns['product_granularity'],
             product_name=client_columns['product_name'],
             quantity_column=client_columns['quantity_column'],
             enhance_diversity=False)