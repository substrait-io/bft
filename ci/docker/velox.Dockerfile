FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/bft/substrait
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip
RUN pip3 install --no-cache --upgrade pip setuptools pytest pyyaml mistletoe pyvelox ruamel.yaml antlr4-python3-runtime pytz

WORKDIR /bft
COPY . .

CMD /usr/bin/python -mpytest bft/tests/test_pyvelox.py
