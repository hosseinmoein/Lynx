FROM python:3.6.5

RUN apt-get update && apt-get -y install \
    ca-certificates \
    curl \
    vim

RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb
RUN echo "9af7440986893c904f24c086c50846ddc5a0f24864f5566b747b8f1a17f7fd52 "\
         "dumb-init_1.2.0_amd64.deb" | sha256sum -c -
RUN dpkg -i dumb-init_1.2.0_amd64.deb

RUN pip install --upgrade --index https://devpi.kensho.com/simple/ kensho-deps

RUN pip install --upgrade setuptools pipenv
ADD app/Pipfile /app/Pipfile
ADD app/Pipfile.lock /app/Pipfile.lock
WORKDIR /app
RUN pipenv install --deploy --system
ADD app/ /app
ENV PYTHONPATH /app

ENTRYPOINT ["dumb-init", "--"]
