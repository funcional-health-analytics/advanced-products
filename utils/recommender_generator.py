import pandas as pd
import logging
import turicreate as tc
import utils.write_to_s3 as ws3
from ds_colombia.recommendation_system import recsys


def recommender(df,
                bucket,
                products_path,
                model_path,
                report_date,
                sales_columns,
                customers_columns,
                products_columns,
                customer,
                n_recommendations,
                customer_column,
                product_granularity,
                product_name,
                quantity_column,
                enhance_diversity=False):
    # TODO: passar a funçao mba reports como parametro
#     if customer == 'comfandi':
#         from utils.comfandi_reports import recsys_reports
#     elif customer == 'farmatodo':
#         from utils.farmatodo_reports import recsys_reports
#     elif customer == 'colsubsidio':
#         from utils.colsubsidio_reports import recsys_reports
    
    # Separate DFs that will be used for the recommender algorithm
    sales = df[sales_columns]
    customers = df[customers_columns]
    products = df[products_columns]

    # Adjust columns data types
    for col in sales.columns:
        sales[col] = sales[col].astype(str)

    for col in customers.columns:
        customers[col] = customers[col].astype(str)

    for col in products.columns:
        products[col] = products[col].astype(str)

    # prepare DFs for the model. Turicriate requires the structure SFrame
    sales = recsys.prepare_sales(sales, customers_columns[0], products_columns[0])
    actions = recsys.dataframe_to_sframe(sales)
    user_data = recsys.dataframe_to_sframe(customers)
    item_data = recsys.dataframe_to_sframe(products)
     
    logging.info("---------------------")
    logging.info("Print Sales")
    logging.info("---------------------")
    
    logging.info(sales.shape)
    logging.info(actions.shape)
    logging.info(user_data)
    logging.info(item_data)
    
    logging.info("---------------------")
    logging.info("---------------------")
    # model fitting
    ranking_factorization_model = recsys.fit_ranking_factorization_recommender(
        actions, customers_columns[0], products_columns[0], user_data, item_data
    )
    logging.info("---------------------")
    logging.info("ranking_factorization_model")
    logging.info("---------------------")
    
    logging.info(ranking_factorization_model)
    
    logging.info("---------------------")
    logging.info("---------------------")
    # saving model to s3, in case it needs debugging or analysis
    #rec_model_path = f"{model_path}/{customer}/{report_date}/{report_date}_{customer}_recommendation_model.model"
    #ws3.save_model_to_s3(ranking_factorization_model, bucket, rec_model_path)

    # extracting recommendations if enhanced, we must compute more recommendations than we actually desire
    if enhance_diversity:
        computed_rec = 2*n_recommendations
    else:
        computed_rec = n_recommendations
    
    recommendations = recsys.make_recommendations(ranking_factorization_model,
                                                  n_recommendations=computed_rec,
                                                  exclude_known=False)
    logging.info("---------------------")
    logging.info("recommendations 1")
    logging.info("---------------------")
    
    logging.info(recommendations)
    
    logging.info("---------------------")
    logging.info("---------------------")
    # small algorithm developed to enhance th recommendations diversity. It's quite slow
    
    if enhance_diversity:
        def str_process(x):
            """
            Function to treat the names of the prducts
            """
            x = x.lower()
            x = x.strip()
            x = x.replace('  ', ' ')
            x = x.replace(' ', '_')
            x = re.sub(r"[^a-zA-Z0-9-/-_]+", '', x)
            return x
        
        def get_distance(x, products):
            """
            Substitute similar products by the one with better score within the recommendations
            of a customer
            """
            if x == products[0]:
                return x
            else:
                for i, product in enumerate(products):
                    dist = tc.toolkits.distances.levenshtein(product, x)
                    if dist < 15:
                        return product
                return x
            
        # imports only needed for the enhanced diversity
        import re
        from tqdm import tqdm
        
        # add the product name to the recommendation list
        grouped_df = df.groupby([product_granularity,
                                 product_name])[quantity_column].sum().reset_index()

        grouped_df = grouped_df.drop_duplicates([product_granularity])

        recommendations[product_granularity] = recommendations[product_granularity].astype(str)
        
        grouped_df[product_granularity] = grouped_df[product_granularity].astype(str)

        recommendations = pd.merge(recommendations, grouped_df, how='left', on=product_granularity)
        
        recommendations[product_name] = recommendations[product_name].apply(str_process)
        
        logging.info("---------------------")
        logging.info("recommendations 2")
        logging.info("---------------------")
    
        logging.info(recommendations)
    
        logging.info("---------------------")
        logging.info("---------------------")
        
        # prepare the DF
        stuff = []
        location = 0
        recommendations = recommendations[recommendations[product_name] != 'n/a']
        ''' 
        for each custumer, go through its recommended products,
        find if there are products way too similar in the list
        substitute similar products by its equivalent with best score
        drop the similar products and return the as many products as the number of
        recommendations desired in the function call
        '''
        for _ in tqdm(recommendations[customer_column].unique()):
            customer_df = recommendations.loc[location:location+computed_rec]
            customer_df['eq_product'] = customer_df[product_name].apply(get_distance,
                                                                        args=(customer_df[product_name].values,))
            customer_df = customer_df.drop_duplicates('eq_product')
            customer_df = customer_df.reset_index(drop=True)
            customer_df['rank'] = customer_df.index+1
            customer_df = customer_df[customer_df['rank'] <= n_recommendations]
            stuff.append(customer_df)
            location = location+20
        
        logging.info("---------------------")
        logging.info("stuff 2")
        logging.info("---------------------")
    
        logging.info(stuff)
    
        logging.info("---------------------")
        logging.info("---------------------")

        recommendations = pd.concat(stuff, ignore_index=True)
        recommendations = recommendations.drop(['eq_product', quantity_column], axis=1)
        logging.info("---------------------")
        logging.info("recommendations 3")
        logging.info("---------------------")
    
        logging.info(recommendations)
    
        logging.info("---------------------")
        logging.info("---------------------")

    #from IPython import embed; embed()
    
    ids = dict(zip(df['product_id'], df['product_name']))
    
    #habead_data_dict = dict(zip(df["customer_id"], df["customer_autorization"]))
    recommendations['product_names'] = 'Name not found'
    recommendations['habeas_data'] = 'Name not found'
    recommendations['product_id'] = recommendations['product_id'].astype(int)
    #recommendations['customer_id'] = recommendations['customer_id'].astype(int)
    #habead_data_dict = dict(zip(df["customer_id"], df["customer_autorization"]))

    for index, row in recommendations.iterrows():
        try:
            recommendations.at[index,'product_names'] = ids[row['product_id']]
            #recommendations.at[index,'habeas_data'] = habead_data_dict[row['customer_id']]
        except:
            continue

    logging.info("---------------------")
    logging.info("Print do shape do recomendations")
    logging.info("---------------------")
    logging.info(recommendations)
    rec_path = f"{products_path}/{customer}/{report_date}/{report_date}_{customer}_recommendations.csv"
    
    logging.info("---------------------")
    logging.info("Print do rec_path")
    logging.info("---------------------")
    logging.info(rec_path)
    ws3.write_csv_to_s3(recommendations, bucket, rec_path)
