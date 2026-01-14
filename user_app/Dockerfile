FROM python:3.10

COPY ./user_app /user_app
WORKDIR /

RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y default-mysql-client
RUN pip install --upgrade pip
RUN pip install -r user_app/requirements.txt

EXPOSE 5000

CMD ["python3", "-u", "-m", "flask", "-A", "user_app/app", "run", "--host", "0.0.0.0", "-p", "5000", "--debug"]
