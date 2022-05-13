FROM python:alpine

WORKDIR /vinod/workdir

COPY ./main.py ./
COPY ./mydb.sqlite3 ./

ENTRYPOINT ["python", "main.py"]

