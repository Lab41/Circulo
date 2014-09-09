FROM python:3

RUN apt-get update
RUN apt-get install --assume-yes git openssl curl 
RUN apt-get install --assume-yes gcc g++ gfortran 
RUN apt-get install --assume-yes libopenblas-dev liblapack-dev 
RUN apt-get install --assume-yes libigraph0
RUN apt-get install --assume-yes libpng12-dev libfreetype6-dev

RUN git clone https://github.com/lab41/circulo.git

WORKDIR /Circulo
RUN CFLAGS='-Wno-error=declaration-after-statement' pip3 install -r requirements.txt

CMD /bin/bash
