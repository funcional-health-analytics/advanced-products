FROM python:3.7-slim


COPY . app/
#RUN pip3 install mlxtend --user
RUN pip3 install -e app/ds-colombia
RUN pip3 install -r app/requirements.txt

WORKDIR app

COPY production.sh .
RUN chmod +x ./production.sh
ENTRYPOINT ["./production.sh"]