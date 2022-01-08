FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=application.py
ENV DB_PATH=db/database.db

EXPOSE 4000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4000"]
