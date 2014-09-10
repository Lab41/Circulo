FROM python:3

RUN apt-get update && apt-get install --assume-yes git openssl curl \ 
     						   gcc g++ gfortran \ 
           					   libopenblas-dev liblapack-dev \
						   libigraph0 \ 
 						   libpng12-dev libfreetype6-dev

ENV CFLAGS '-Wno-error=declaration-after-statement'
RUN pip3 install numpy scipy scikit-learn matplotlib python-igraph

ADD . /Circulo
WORKDIR /Circulo
RUN pip3 install -r requirements.txt
ENV PYTHONPATH /Circulo

CMD /bin/bash
