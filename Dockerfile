FROM python:3

RUN apt-get update
RUN apt-get install --assume-yes git openssl curl gcc g++ gfortran libopenblas-dev liblapack-dev libigraph0 libpng12-dev libfreetype6-dev

ADD . /Circulo
WORKDIR /Circulo
RUN CFLAGS='-Wno-error=declaration-after-statement' pip3 install -r requirements.txt

CMD /bin/bash
