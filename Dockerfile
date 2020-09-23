FROM python:3.8-alpine

ADD . /cardmarket_exporter
WORKDIR /cardmarket_exporter

RUN pip install -r requirements.txt

CMD /cardmarket_exporter/cardmarket_exporter.py