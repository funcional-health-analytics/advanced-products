import utils.write_to_s3 as ws3
import logging
from ds_colombia.anomaly_detector.anomaly_functions import (find_suspects,
                                                            get_transactions_last_month,
                                                            get_reference_table)
from utils.data_cleaning import anomaly_data_cleaning


def anomaly_detector(df,
                     bucket,
                     products_path,
                     report_date,
                     anomaly_product_granularity,
                     product_name,
                     date_column,
                     quantity_column,
                     order_column,
                     customer_column,
                     store_granularity,
                     stddev,
                     customer):
    
    logging.info("---------------------------------")
    logging.info("Primeira funcao")
    logging.info("---------------------------------")
    
    df, excluded = anomaly_data_cleaning(df, customer_column, date_column)
    
    logging.info("---------------------------------")
    logging.info("Segunda funcao")
    logging.info("---------------------------------")

    transactions_last_month, sparse_matrix_last_month = get_transactions_last_month(full_view = df,
                                                                                    customer_column=customer_column,
                                                                        product_granularity=anomaly_product_granularity,                                                                           quantity_column=quantity_column,
                                                                        date_column = date_column)
    logging.info("---------------------------------")
    logging.info("terceira funcao")
    logging.info("---------------------------------")
    reference_table = get_reference_table(df,
                                          customer_column,
                                          anomaly_product_granularity,
                                          quantity_column,
                                          date_column)
    
    logging.info("---------------------------------")
    logging.info("Quarta funcao")
    logging.info("---------------------------------")
    df_suspects = find_suspects(transactions_last_month,
                                sparse_matrix_last_month,
                                reference_table,
                                stddev,
                                customer_column=customer_column,
                                store_column=store_granularity,
                                product_granularity=anomaly_product_granularity,
                                product_name=product_name,
                                quantity_column=quantity_column,
                                date_column=date_column)

    logging.info("---------------------------------")
    logging.info("Salvando os dados")
    logging.info("---------------------------------")
    
    suspects_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_anomalies.xlsx"
    ws3.write_xlsx_to_s3(df_suspects, bucket, suspects_path)

    logging.info("---------------------------------")
    logging.info("Done")
    logging.info("---------------------------------")