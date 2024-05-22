FROM python:3.11-slim-buster

# CRIAR IMAGEM: docker build -t juntardinheiro:1.0 .
# CRIAR CONTAINER: docker-compose up -d
# EXCLUIR CONTAINER: docker container rm -f juntardinheiro
# EXCLUIR IMAGEM: docker image rm juntardinheiro:1.0
# EXECUTAR TESTE: docker exec -it juntardinheiro pytest .

LABEL maintainer="Copyright 2024 Taylor Lopes <taylorlopes@gmail.com>"

# Install packages
RUN set -x \
   && apt-get update \
   && apt-get upgrade -y \
   && apt-get install -y curl gnupg wget unzip gcc

# sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev

# Driver ODBC MSSQL
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y ca-certificates msodbcsql17 unixodbc unixodbc-dev
  
# Clean
RUN apt-get purge -y --auto-remove \
   && rm -rf /var/lib/apt/lists/* /tmp/*

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore

COPY . /app

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt 