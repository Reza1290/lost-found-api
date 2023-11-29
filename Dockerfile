FROM python:3.11.4

WORKDIR /

COPY . .

EXPOSE 8080

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:8084 api:app
