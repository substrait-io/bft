FROM alpine:3.18

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/bft/substrait
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools pytest pyyaml mistletoe duckdb ruamel.yaml antlr4-python3-runtime pytz

WORKDIR /bft
COPY . .

CMD /usr/bin/python -mpytest bft/tests/test_duckdb.py
