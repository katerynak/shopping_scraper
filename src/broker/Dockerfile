FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/

RUN pip install mongoengine
RUN pip install redis
RUN pip install python-Levenshtein


COPY ./data_collections ./data_collections
COPY ./data_processing/product_similarity.py ./data_processing/
COPY ./broker .
RUN chown -R user:user /home/user
USER user

CMD [ "python", "main.py"]