import pandas as pd
import numpy as np
import logging


def mba_data_cleaning(df,
                      product_granularity,
                      product_group = '',
                      allowed_product_types = []):
    """Gets the data frame that will be used for the MBA analysis and removes products with invalid ids (-1)
    and also products that belong to groups that are not allowed to enter the algorithm

    Parameters
    ----------
    df : DataFrame
        The Data Frame that will be used in the MBA analysis
    product_granularity : str
        Name of the column that contains the product ids
    product_group : str, optional
        Name of the column that contains the category of the product and is subject to exclusion
    allowed_product_types : list, optional
        List of the allowed categories

    Returns
    -------
    df
        The Data Frame that will be used for the MBA analysis
    excluded_df
        A Dataframe with the products that were excluded from the analysis and how much they sold
    """
    excluded_df = df[df[product_granularity] == -1][product_granularity].to_frame()
    excluded_df['exclusion reason'] = 'invalid id'
    df = df[df[product_granularity] != -1]
    if allowed_product_types:
        bad_cat_df = df[~df[product_group].isin(allowed_product_types)][product_granularity].to_frame()
        bad_cat_df['exclusion reason'] = 'forbidden category'
        df = df[df[product_group].isin(allowed_product_types)]
        excluded_df = pd.concat([excluded_df, bad_cat_df])
    excluded_df = excluded_df.groupby([product_granularity, 'exclusion reason']).size().reset_index(name='number of sales')
    return df, excluded_df


def clv_data_cleaning(df,
                      date_column,
                      value_column, 
                      customer_column):

    last_year = (df[date_column].max() - pd.DateOffset(months=12))
    
    logging.info('step1')
    end_date = df[date_column].max()
    
    logging.info('step2')
    df = df[df[date_column] >= last_year]
    
    logging.info('step3')
    bad_values_mask = (df[value_column].isna()) |\
                      (df[value_column] < 0)
    bad_values_df = df[bad_values_mask]
    bad_values_df['reason'] = 'invalid sale value'
    df = df[~bad_values_mask]

    # filter missing values from the
    # client id column
    bad_ids_mask = (df[customer_column] == -1)
    bad_ids_df = df[bad_ids_mask]
    bad_ids_df['reason'] = 'invalid customer id'
    excluded_df = pd.concat([bad_values_df, bad_ids_df])
    df = df[~bad_ids_mask]
    return df



def anomaly_data_cleaning(df, customer_column, date_column):
    excluded_df = df[(df[customer_column] != "N/A") |\
                     (df[customer_column] != -1) |\
                     (df[date_column]<"2020-06")]
    df = df[df[customer_column] != "N/A"]
    df = df[df[customer_column] != -1]
    df = df[df[date_column]<"2020-06"]
    return df, excluded_df