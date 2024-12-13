FROM python:3.9-slim

RUN apt-get update && apt-get install -y netcat-openbsd

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD sh -c "while ! nc -z mysql 3306; do sleep 1; done; \
            flask db init && flask db migrate -m 'Initial migration' && flask db upgrade && \
            gunicorn -b 0.0.0.0:3000 app:app"
