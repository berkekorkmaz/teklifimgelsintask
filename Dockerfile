FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV FLASK_APP=app/routes.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"] 