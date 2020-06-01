FROM buildpack-deps:buster

LABEL Author = Gianfranco
LABEL E-mail = "gianfranco.ferracci@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY /Concorso/. /app/Concorso
COPY . /app

EXPOSE 5555
ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]