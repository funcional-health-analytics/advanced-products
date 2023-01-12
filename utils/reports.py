import pandas as pd
import numpy as np
import logging

def mba_reports(df, 
                rules,
                rec_table,
                product_granularity, 
                product_name, 
                value_column):
    """Format the DataFrames so they can be sent to Comfandi

    Parameters
    ----------
    df : DataFrame
        DataFrame of sales
    rules : DataFrame
        DataFrame containing th MBA rules
    rec_table : DataFrame
        DataFrame containing th MBA combinations
    product_granularity : str
        string with the product granularity column
    product_name : str
        string with the product name column
    value_column : str
        string with the sale value column

    Returns
    -------
    rules
        DataFrame containing th MBA rules
    mba_store_df
        DataFrame containing th MBA combinations for offline use
    mba_online_df
        DataFrame containing th MBA combinations for online use
    """

    grouped = df.groupby([product_granularity, product_name]).agg({value_column: 'sum'}).reset_index()
    
    grouped[product_name] = grouped[product_name].replace('N/A', 'name not informed', regex=True)
    

    product_names_dict = dict(zip(grouped[product_granularity], grouped[product_name]))

    mba_recommendation = pd.merge(rec_table, grouped, how='left', left_on='antecedents', right_on = 'product_id')
    mba_recommendation = mba_recommendation.drop('product_id', axis = 1)
    mba_recommendation = mba_recommendation.sort_values(by=[value_column], ascending=False).reset_index()
    mba_recommendation = mba_recommendation.drop('index', axis = 1)
    mba_recommendation['consequents_names'] = ''
    
    for index, row in mba_recommendation.iterrows():
        name_list = []
        for product_id in row['consequents']:
            name_list.append(product_names_dict[product_id])
        mba_recommendation.at[index,'consequents_names'] = name_list

    a = mba_recommendation['consequents'].explode().reset_index()
    mba_recommendation['consequents'] = mba_recommendation['consequents'].apply(lambda x: x[:14] if len(x) > 15 else x)
    mba_recommendation['consequents_names'] = mba_recommendation['consequents_names'].apply(lambda x: x[:14] if len(x) > 15 else x)    
    mba_recommendation = mba_recommendation.explode('consequents_names')
    mba_recommendation = mba_recommendation.reset_index()
    mba_recommendation = mba_recommendation.drop(['index'], axis = 1)
    mba_recommendation['consequents'] = a['consequents']
    
    mba_recommendation = mba_recommendation.rename(columns={"antecedents": "Producto Principal ID",
                                    "consequents": "Producto Recomendado ID",
                                    product_name: "Producto Principal Nombre",
                                    "consequents_names": "Producto Recomendado Nombre",
                                    value_column: "Producto Principal Valor Vendido",
                                   })
    cols = ["Producto Principal ID", "Producto Principal Nombre", 
            "Producto Principal Valor Vendido", "Producto Recomendado ID", "Producto Recomendado Nombre"]
    mba_recommendation = mba_recommendation[cols]

    mba_recommendation = mba_recommendation.set_index(['Producto Principal ID',
                                                       'Producto Principal Nombre',
                                                       'Producto Principal Valor Vendido'])

    product_list = list(dict.fromkeys(mba_recommendation.index.get_level_values('Producto Principal ID').values))
    for product in product_list:
        basket_size = mba_recommendation.loc[product].shape[0] 
        if basket_size <= 4:
            mba_recommendation.loc[product, 'filter'] = 'store'
        elif basket_size > 4:
            mba_recommendation.loc[product, 'filter'] = 'carousel'

    mba_store_df = mba_recommendation[mba_recommendation['filter'] == 'store']
    mba_online_df = mba_recommendation[mba_recommendation['filter'] == 'carousel']
    return rules, mba_store_df, mba_online_df



def recsys_reports(rec_df, products_df, customers_df):
    """

    Parameters
    ----------
    rec_df : DataFrame
        DataFrame
    products_df : DataFrame
        DataFrame 

    Returns
    -------
    rec_df
        DataFrame
    """
    ids = products_df.groupby(['product_id', 'product_description'])['product_large_description'].count().reset_index().drop('product_large_description', axis = 1)
    ids['product_id'] = ids['product_id'].astype(str)
    ids = ids.set_index('product_id').to_dict()
    habead_data_dict = dict(zip(customers_df["customer_id"], customers_df["customer_autorization"]))
    rec_df['product_id'] = rec_df['product_id'].astype(str)
    rec_df['product_names'] = ''
    from IPython import embed; embed()
    for index, row in rec_df.iterrows():
        try:
            rec_df.at[index,'product_names'] = ids[row['product_id']]
            rec_df.at[index,'customer_id'] = ids[row['product_id']]
        except:
            continue
    return rec_df