from ds_colombia.market_basket_analysis.mba import df_to_mba
import logging
from utils.data_cleaning import mba_data_cleaning
import utils.write_to_s3 as ws3
from utils.reports import mba_reports

def mba_generator(df,
                  bucket,
                  products_path,
                  report_date,
                  product_granularity,
                  product_name,
                  product_group,
                  date_column,
                  quantity_column,
                  order_column,
                  value_column,
                  n_products,
                  n_rules,
                  min_support,
                  max_len,
                  allowed_product_types,
                  customer):
    
    logging.info("Cleaning data")
    df, excluded_df = mba_data_cleaning(df,
                                        product_granularity,
                                        product_granularity,
                                        allowed_product_types)

    logging.info("Calculating MBA. This is gonna take a while")
    
    rules, rec_table = df_to_mba(df,
                                 product_column=product_granularity,
                                 quantity_column=quantity_column,
                                 order_column=order_column,
                                 n_products=n_products,
#                                n_rules = n_rules,
                                 min_support=min_support,
                                 max_len=max_len,
                                 use_colnames=True)


    
    logging.info("Preparing MBA output tables")
    rules, mba_store_df, mba_online_df = mba_reports(df,
                                                     rules,
                                                     rec_table,
                                                     product_granularity,
                                                     product_name,
                                                     value_column)

    logging.info("Saving MBA reports (mba_rules and mba_recommendations) and exclusion report")
    excluded_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_excluded_mba.xlsx"
    ws3.write_xlsx_to_s3(excluded_df, bucket, excluded_path)
    
    logging.info("Saving rules..........")
    rules_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_rules.xlsx"
    if ((rules.shape[0]<1048576) and (rules.shape[1]<16384)):
        ws3.write_xlsx_to_s3(rules, bucket, rules_path)
    else:
        rules_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_rules.csv"
        ws3.write_csv_to_s3(rules, bucket, rules_path)
#     from IPython import embed; embed()
    mba_path_stores = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_recommendations_stores.xlsx"
    mba_path_online = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_recommendations_online.xlsx"
    
    logging.info("Saving store or online..........")
    if not mba_store_df.empty:
        if ((mba_store_df.shape[0]<1048576) and (mba_store_df.shape[1]<16384)):
            ws3.write_xlsx_to_s3(mba_store_df, bucket, mba_path_stores, sheet_name='action plan stores')
        else:
            mba_path_stores = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_recommendations_stores.csv"
            ws3.write_csv_to_s3(mba_store_df, bucket, mba_path_stores)
    if not mba_online_df.empty:
        if ((mba_online_df.shape[0]<1048576) and (mba_online_df.shape[1]<16384)):
            ws3.write_xlsx_to_s3(mba_online_df, bucket, mba_path_online, sheet_name='action plan online')
        else:
            mba_path_online = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_mba_recommendations_online.csv"
            ws3.write_csv_to_s3(mba_online_df, bucket, mba_path_online)
    
