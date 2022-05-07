FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /home/

RUN sh -c 'apt-get update  -y  && apt-get install  curl gcc g++ python3-dev musl-dev git -y && apt-get clean -y'

COPY Pipfile* /home/

RUN git config --global http.sslverify false

RUN pip install --upgrade pip

RUN pip install  pipenv 

RUN pipenv install --system --deploy

COPY . /home/

USER root

EXPOSE 8080

ENTRYPOINT ["python", "-m"]

CMD ["app.main"]