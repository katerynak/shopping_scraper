FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/

RUN pip install --no-cache-dir mongoengine==0.20.0
RUN pip install --no-cache-dir redis==3.5.3
RUN pip install --no-cache-dir flask==1.1.2

COPY ./client .
COPY ./data_collections ./data_collections

RUN chown -R user:user /home/user
USER user
