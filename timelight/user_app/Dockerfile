FROM python:3.10

COPY . /user_app

WORKDIR /
RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip install --upgrade pip
RUN apt-get install -y default-libmysqlclient-dev
RUN pip install -r requirements.txt
RUN apt-get install -y default-mysql-client

EXPOSE 5000

#CMD ["python3", "-u", "-m", "flask", "run", "--host", "0.0.0.0", "-p", "5000", "--debug"]

WORKDIR /

ENTRYPOINT ["python3", "-u", "-m", "gunicorn", "-w", "4", "user_app.app:app"]
