FROM python:3.8-slim-buster

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=application.py
ENV DB_PATH=database.db

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4000"]