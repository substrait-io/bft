FROM postgres:15-alpine
ENV POSTGRES_DB=bft
ENV POSTGRES_PASSWORD=postgres

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/bft/substrait
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools pytest pyyaml mistletoe psycopg[binary] ruamel.yaml antlr4-python3-runtime pytz

WORKDIR /bft
COPY . .

CMD /usr/bin/python -mpytest bft/tests/test_postgres.py
