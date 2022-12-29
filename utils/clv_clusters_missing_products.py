from datetime import datetime
import logging
from ds_colombia.clv.clv_churn import df_to_clv
import utils.write_to_s3 as ws3
from ds_colombia.product_suggestions.product_suggestions import (prepare_cluster_data,
                                                                 make_pareto_cluster,
                                                                 make_pareto_store,
                                                                 make_pareto_store_cluster,
                                                                 make_missing_products_table)
from utils.data_cleaning import clv_data_cleaning


def clv_cluster_missing_products(df,
                                 bucket,
                                 products_path,
                                 report_date,
                                 product_granularity,
                                 product_name,
                                 date_column,
                                 quantity_column,
                                 order_column,
                                 customer_column,
                                 store_granularity,
                                 value_column,
                                 end_date,
                                 period_months,
                                 customer):

    logging.info("Computing CLV\n")
    sales = clv_data_cleaning(df, date_column, value_column, customer_column)
    
    logging.info("Step 1\n")
    
    clv_t = df_to_clv(sales,
                    customer_column,
                    date_column,
                    value_column,
                    end_date,
                    penalizer_coef=0,
                    period=period_months,
                    discount_rate=0.0,
                    clv_group_ranges =[0, 0.5, 0.80, 0.9375, 0.98435, 1],
                    clv_group_labels =['Low-Low', 'Low', 'Medium', 'High', 'High-High'],
                    churn_groups_bins=3,
                    churn_groups_labels = ['churn', 'medium', 'alive'])

    logging.info("Step 2\n")
    
    clv = clv_t[0].reset_index().rename(columns={"id": customer_column})

#     logging.info("Saving CLV table to excel")
#     excluded_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_excluded_clv_churn.xlsx"
#     ws3.write_xlsx_to_s3(excluded_df, bucket, excluded_path)
    
    clv_path = f"{products_path}/{customer}/{report_date}/{customer}_clv_churn.xlsx"
    ws3.write_xlsx_to_s3(clv, bucket, clv_path)

#     parquet_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_clv_churn.parquet.gzip"
#     ws3.write_parquet_to_s3(clv, bucket, parquet_path)

    #logging.info("Reading files to compute Missing Products")

    # Rename group here to avoid having to modify prepare_cluster_data function
    clv = clv.rename(columns={"clv_group": "group"})

    df = sales.merge(clv, on=customer_column)

    #logging.info("Computing Paretos for Missing Products")

    df = prepare_cluster_data(df)

    cluster_pareto = make_pareto_cluster(df,
                                         quantity_column,
                                         product_granularity,
                                         pareto_percentage_cluster=50)

    store_pareto = make_pareto_store(df,
                                     quantity_column,
                                     product_granularity,
                                     store_granularity,
                                     pareto_percentage_store=101)

    store_cluster_pareto = make_pareto_store_cluster(df,
                                                     quantity_column,
                                                     store_granularity,
                                                     pareto_percentage_store_clusters=80)

    missing_prod = make_missing_products_table(
        store_pareto, store_cluster_pareto, cluster_pareto, store_granularity, product_granularity
    )

    #logging.info("Saving Missing Products table to Excel")
    missing_prod_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_CLV_missing_products.xlsx"
    ws3.write_xlsx_to_s3(missing_prod, bucket, missing_prod_path)
    logging.info("Done")
