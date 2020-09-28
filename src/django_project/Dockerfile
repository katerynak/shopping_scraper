FROM python:3-buster

RUN useradd --shell /bin/bash user --create-home -d /home/user/
WORKDIR /home/user/

RUN pip install --no-cache-dir mongoengine==0.20.0
RUN pip install --no-cache-dir redis==3.5.3
RUN pip install --no-cache-dir django==3.1.1

COPY ./django_project .
COPY ./data_collections ./data_collections

RUN chown -R user:user /home/user
USER user

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]