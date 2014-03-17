FROM ubuntu:12.10
MAINTAINER Alex Brandt <alunduil@alunduil.com>

RUN apt-get update
RUN apt-get upgrade -y -qq

RUN apt-get install -y -qq python-pip

ADD conf /etc/margarine

ADD . /usr/local/src/margarine

RUN pip install -q -r /usr/local/src/margarine/requirements.txt

WORKDIR /usr/local/src/margarine

RUN python setup.py -q install

RUN useradd -c 'added by docker for margarine' -d /usr/local/src/margarine -r margarine
USER margarine

EXPOSE 5000

ENTRYPOINT [ "/usr/local/bin/margarine" ]
CMD [ "tinge", "blend", "spread" ]
