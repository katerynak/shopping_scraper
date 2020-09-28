FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/


RUN pip install --no-cache-dir scrapy
RUN pip install --no-cache-dir mongoengine
RUN pip install --no-cache-dir redis
RUN pip install --no-cache-dir pillow
RUN pip install --no-cache-dir python-Levenshtein


COPY ./data_collections ./data_collections
COPY ./data_processing/product_similarity.py ./
COPY ./crawling .
RUN mkdir /home/user/images
RUN chown -R user:user /home/user
USER user

CMD ["python", "main.py"]