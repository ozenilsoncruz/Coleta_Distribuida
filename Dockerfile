FROM python:3.9-slim-buster

WORKDIR /

COPY /requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=api.py

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]