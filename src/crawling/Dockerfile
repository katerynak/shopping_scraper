FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/


RUN pip install scrapy
RUN pip install mongoengine
RUN pip install redis
RUN pip install pillow


COPY . .
RUN chown -R user:user /home/user
USER user

RUN mkdir /home/user/images

CMD [ "python", "main.py"]