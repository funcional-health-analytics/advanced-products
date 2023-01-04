FROM python:3.7-slim

COPY . app/
#RUN pip3 install mlxtend --user
RUN apt-get update && apt-get install -y git
RUN pip3 install -e git+https://afflorezr2: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@github.com/funcional-health-analytics/advanced-products-pkg.git@main#egg=ds_colombia
RUN pip3 install -r app/requirements.txt
RUN pip3 install "snowflake-connector-python[pandas]"
         


WORKDIR app

COPY production.sh .
RUN chmod +x ./production.sh
ENTRYPOINT ["./production.sh"]