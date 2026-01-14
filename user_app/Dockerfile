FROM python:3.10

COPY . /user_app
WORKDIR /user_app

RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y default-mysql-client
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3", "-m", "flask", "-A", "app", "run", "--host", "0.0.0.0", "-p", "5000"]
