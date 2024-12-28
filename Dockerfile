FROM continuumio/miniconda3

RUN apt-get update

# Required for udacidrone -> pymavlink
RUN apt-get install -y gcc libxml2-dev libxslt-dev

WORKDIR /app

COPY environment.yml environment.yml

RUN conda env create -f environment.yml
# make fcnd to be activated by default
RUN echo "conda activate fcnd" >> ~/.bashrc

CMD [ "bash" ]
