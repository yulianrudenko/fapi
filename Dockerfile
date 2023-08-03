FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /home/web

COPY ./requirements.txt /home/web/requirements.txt
RUN pip install -r /home/web/requirements.txt

COPY ./app /home/web/app