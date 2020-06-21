# FROM buildpack-deps:buster
# FROM python:3.8.3-slim-buster
FROM tiangolo/meinheld-gunicorn:python3.7

LABEL Author = Gianfranco
LABEL E-mail = "gianfranco.ferracci@gmail.com"

# RUN apt-get update -y && \
#    apt-get install -y python3-pip python3-dev && \
#    apt-get install -y gunicorn

# RUN apt-get update -y 

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY /Concorso/. /app/Concorso
COPY . /app

# EXPOSE 8000 5000
EXPOSE 8000 5000

# ENTRYPOINT [ "python3" ]
# CMD [ "app.py" ]

# ENTRYPOINT [ "gunicorn" ]
# CMD [ "Concorso:app" ]


# CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "Concorso:app"]

# ENTRYPOINT ["bash"]
# CMD ["gunicorn Concorso:app"]
# CMD ["sudo gunicorn Concorso:app"]
# CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "Concorso:app"]