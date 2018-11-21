FROM hseling/hseling-api-base:python3.6-alpine3.7

LABEL maintainer="Sergey Sobko <ssobko@hse.ru>"

COPY ./app /app
COPY ./hseling_api_nauchpop /app/hseling_api_nauchpop
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
