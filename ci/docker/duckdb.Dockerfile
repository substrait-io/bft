FROM alpine:latest

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools pytest pyyaml mistletoe duckdb

WORKDIR /bft
COPY . .

CMD /usr/bin/python -mpytest bft/tests/test_duckdb.py
