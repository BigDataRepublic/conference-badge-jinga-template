FROM python:3.9-slim-buster

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app

WORKDIR /app

CMD ["flask", "--app=main", "run", "--port=80", "--host=0.0.0.0", "--debugger", "--reload"]