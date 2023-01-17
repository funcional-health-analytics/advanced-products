# Advanced-Products
In this project we run four algorithms to understand sale's data, they are:

## MBA
## CLV
## Recomendations
## Anomalies

# Architecture
# Execution
```json
 {
    "priority": "HIGH",
    "parameters": {
			  "MBA":"True",
				"CLV":"True",
			  "AD":"False",
			  "RECOMMENDER":"False",
        "MEMORY": "10000",
        "memoryReservation":"10000",
        "privileged":"true"
    }
 }
```
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
Uma vez logado é possível subir a imagem para o ECR com:

```
docker push 997206602955.dkr.ecr.us-east-1.amazonaws.com/lupa
```
Ou
```
sudo docker push 997206602955.dkr.ecr.us-east-1.amazonaws.com/lupa
```

### Executar o processo

O processo será executado no AWS BATCH. Para poder executá-lo deverá ser feito uma requisição
`POST` no ARAUTO. Abaixo um exemplo utilizando o curl para realizar esta chamada.

Nessa nova versão foram incluídos os parametros "SERVER" para a seleção do server que será considerado("POSTGRESQL" ou "MSSQL"), "OPERADORA" para filtro de operadora específica("todas", "PORTO SAUDE", "GNDI", "SULAMERICA", etc.) e "GRUPO CLIENTE" para, no caso de usarmos o banco POSTGRESQL, escolher o cliente atendido pela funcional (e.g., "PORTO SEGURO", "Seguros Unimed"). Se a operadora informada não for encontrada para o cliente selecionado, a aplicação será realizada considerando todas as operadoras.

```
curl -X POST \
  https://d2lbvqo36md01z.cloudfront.net/jobs/lupa \
  -H 'Content-Type: application/json' \
  -d '{
    "priority": "DEFAULT",
    "parameters": {
        "MEMORY": "10000",
        "memoryReservation":"10000",
        "privileged":"true",
        "LOGO": "logo_funcional",
        "SERVER": "POSTGRESQL",
        "DBNAME": "HA_Relacional", 
        "GRUPO_CLIENTE": "PORTO SEGURO",
        "EMPRESA": "EMPRESA-99.556.534",
        "OPERADORA": "PORTO SAUDE" 
    }
}'
```



Os principais parâmetros são os seguintes:
- `LOGO`: qual logo será estampado no relatório. Os valores possíveis são: `logo_funcional`, `logo_itechcare` ou `logo_qualicorp`
- `SERVER`: O tipo de servidor de DB a ser usado ("POSTGRESQL" ou "MSSQL").
- `DBNAME`: Qual o nome do DB do cliente dentro do MSSQL ou Postgres
- `GRUPO_CLIENTE`: O nome do grupo cliente (i.e., o cliente da Funcional). Obrigatório apenas se SERVER = POSTGRESQL.
- `EMPRESA`: O nome da empresa dentro do grupo cliente.
- `OPERADORA`: Filtro de operadora específica("todas", "PORTO SAUDE", "GNDI", "SULAMERICA", etc.). Opcional.

### Output

O output estará no S3 no bucket `fnc-reports`


### Executar o processo localmente (Novo!)

O processo será executado no prompt. Para poder executá-lo deverá ser feito um arquivo teste.env onde será colocado os parametros necessários para executar o container. Lembrando que o arquivo não deve estar na raiz do projeto. Abaixo um exemplo de como o arquivo teste.env deve ser preenchido:

```
VAR_AWS=1
LOGO=logo_itechcare
SERVER=MSSQL
DBNAME=DW_GestaoIntegrada_GrupoCase
GRUPO_CLIENTE=<Obrigatório apenas se SERVER = POSTGRESQL.>
EMPRESA=BRF
OPERADORA=todas
HOST=<Host do BD>
USUARIO=<Usuario do BD>
PASSWORD=<Senha do BD>
```

Agora iremos executar o container da seguinte forma:

```
sudo docker run --env-file=<pasta do arquivo>/teste.env -v <pasta de saida do lupa>:/data 997206602955.dkr.ecr.us-east-1.amazonaws.com/lupa
```

Na linha de execução temos os seguintes argumentos:
- `--env-file=`: Indica a localização das variveis de ambiente necessárias para o processo 
(ex: --env-file=/home/kevin/lupa_entrada/teste.env)
- `-v`: Cria um volume onde o container pode se comunicar com o host, assim nossa pasta de saída vai ter tudo que for gravado na pasta '/data' dentro do container (ex: -v /home/kevin/lupa_saida:/data)

Os parâmetros do arquivo teste.env são os seguintes:
- `VAR_AWS`: É uma variavel fixa para rodar o processo localmente (impede os processos da AWS)
- `LOGO`: qual logo será estampado no relatório. Os valores possíveis são: `logo_funcional`, `logo_itechcare` ou `logo_qualicorp`
- `SERVER`: O tipo de servidor de DB a ser usado ("POSTGRESQL" ou "MSSQL").
- `DBNAME`: Qual o nome do DB do cliente dentro do MSSQL ou Postgres
- `GRUPO_CLIENTE`: O nome do grupo cliente (i.e., o cliente da Funcional). Obrigatório apenas se SERVER = POSTGRESQL.
- `EMPRESA`: O nome da empresa dentro do grupo cliente.
- `OPERADORA`: Filtro de operadora específica("todas", "PORTO SAUDE", "GNDI", "SULAMERICA", etc.). Opcional.
- `HOST`: O host do Banco de Dados.
- `USUARIO`: O usuário do Banco de Dados.
- `PASSWORD`: O senha do Banco de Dados.

