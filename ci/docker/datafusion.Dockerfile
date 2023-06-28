FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y python3.10 && ln -sf python3 /usr/bin/python
RUN apt install -y pip
RUN pip install --upgrade pip setuptools pytest pyyaml mistletoe datafusion

WORKDIR /bft
COPY . .

CMD /usr/bin/python -mpytest bft/tests/test_datafusion.py
