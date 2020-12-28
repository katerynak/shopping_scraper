FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/


RUN pip install --no-cache-dir scrapy==2.1.0
RUN pip install --no-cache-dir mongoengine==0.20.0
RUN pip install --no-cache-dir redis==3.5.3
RUN pip install --no-cache-dir pillow==8.0.1
RUN pip install --no-cache-dir python-Levenshtein==0.12.0

COPY ./crawling .
COPY ./data_collections ./data_collections
COPY ./data_processing/ ./data_processing

RUN mkdir /home/user/images
RUN chown -R user:user /home/user
USER user

# CMD ["python", "main.py"]