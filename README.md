# Advanced-Products
In this project we run four algorithms to understand sale's data, they are:

## MBA: 
Market basket analysis finds out customers’ purchasing patterns by discovering important associations among the products which they place in their shopping baskets. The aim of market basket analysis is to determine which items are frequently purchased together by customers. The term frequent items mean the itemsets which satisfy a user-specified predefined percentage value. For example, if customers have purchased milk in a supermarket, then how many greatly possibility to purchase bread simultaneously with milk. To discover the associations we use **FP-Growth** which is one of the most common algorithms for mining frequent itemsets. Here, the minimum support is needed to satisfy for identifying the frequent itemsets. Some of the main measures used in the algorithm are:

* **Confidence**: 
It is basically conditional probability. If there are items: X and Y, confidence measures the percentage of times item Y was purchased,given that item X was purchased. Confidence values ranges from 0 to 1. Higher confidence value indicates that the item Y will be purchased in more number of cases given that X was purchased.

* **Lift**:
It is the ratio of Confidence / Support of item sets.It is the main measure which is used to determine the usefulness of Market Basket Analysis rule.If Lift of item set is above 1,then the items will be bought together more often. 

* **Conviction**: 
It is similar to lift but unlike lift it is a directed measure.It compares the probability that X appears without Y with the actual frequency of the appearance of X without Y in the transaction data.

* **Leverage** : 
Leverage measures the difference of X and Y appearing together in the data set and what would be expected if X and Y where statistically dependent. It helps in finding how many more units of items X and Y together are sold than expected from the independent sales of X and Y item.
	
This analysis helps the shop owners to take many important business decisions, identify regular customers, increase products sale, catalog design and many more. The main goal of market basket analysis is to extract associations among purchasing products. It also helps retailers to product placement on shelves by placing similar products close to one another. For example, If customers who purchase computers also tend to buy anti-virus software at the same time, then placing the hardware display close to software display may help increase the sale of both items. For more information about MBA see [1] and references therein. 

## CLV
## Recomendations
## Anomalies

# Architecture

## Requirements

This project were developed to work with SnowFlake. The SQL query get the necessary columns to process the algorithms and then the results are saving in the bucket s3:fnc-data-science/test-colombia/products.

## Instruções de uso
To get the results is necessay build and push a Docker image to ECR aws service where aws batch will have access it.

### Building the imagem
The first thing to do is to clone the project from Git Hub repository, after that in the root folder execute:

```
docker build -t 997206602955.dkr.ecr.us-east-1.amazonaws.com/mba .
```
or

```
sudo docker build -t 997206602955.dkr.ecr.us-east-1.amazonaws.com/lupa .
```

***

### Pushing the imagem

Once the image is building is necessary push it to ECR aws service, to do that we need to be logged in aws. To login in aws we use aws-cli with the command:

```
aws sso login
```

then


```
sudo docker login -u AWS -p $(aws ecr get-login-password --region us-east-1 --profile default) 997206602955.dkr.ecr.us-east-1.amazonaws.com
```

***
Once you are logged you are able to push the image to ECR

```
sudo docker push 997206602955.dkr.ecr.us-east-1.amazonaws.com/mba
```

### Execution

The algorithms are executed in aws Batch, to do that it's necessary send a request `Post` for ARAUTO:

```
curl -X POST \
  https://d2lbvqo36md01z.cloudfront.net/jobs/adv-prods \
  -H 'Content-Type: application/json' \
  -d '{
    "priority": "DEFAULT",
    "parameters": {
		   "MBA":"True",
		   "CLV":"True",
		   "AD":"False",
		   "RECOMMENDER":"False",
        	   "MEMORY": "10000",
                   "memoryReservation":"10000",
                   "privileged":"true"
		   }
}'
```


The main parameters are:
- `MBA`: Boolean value indicating if the MBA data analysis is required
- `CLV`: Boolean value indicating if the CLV data analysis is required
- `AD` : Boolean value indicating if the Anomaly Detector data analysis is required
- `RECOMMENDER`: Boolean value indicating if the Recomender data analysis is required


### Output

O output estará no s3:fnc-data-science/test-colombia/products.

## References
1. Market Basket Analysis Using Apriori and FP Growth Algorithm, 22nd International Conference on Computer and Information Technology (ICCIT), 18-20 December, 2019.
