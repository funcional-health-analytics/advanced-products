# Advanced-Products
In this project we run four algorithms to understand sale's data, they are:

## MBA
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
