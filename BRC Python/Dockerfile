FROM python:3.9-slim

RUN apt-get update && apt-get install -y build-essential python3-dev libqt5widgets5-dev libqt5core5-dev libqt5gui5-dev

RUN apt-get install -y mongodb

RUN service mongodb start \
    && mongo admin --eval 'db.createUser({user: "sid", pwd: "test", roles: [{role: "userAdminAnyDatabase", db: "admin"}]})' \
    && service mongodb stop

RUN echo "mysql-server mysql-server/root_password password sidh34" | debconf-set-selections
RUN echo "mysql-server mysql-server/root_password_again password sidh34" | debconf-set-selections
RUN apt-get install -y mysql-server

WORKDIR /app

COPY . /app

RUN python3 -m pip install .

CMD ["python3", "main.py"]