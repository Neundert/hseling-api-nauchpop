FROM hseling/hseling-api-base:python3.6 as build

LABEL maintainer="Sergey Sobko <ssobko@hse.ru>"

RUN mkdir /dependencies
COPY ./requirements.txt /dependencies/requirements.txt
COPY ./setup.py /dependencies/setup.py
RUN pip install -r /dependencies/requirements.txt

FROM hseling/hseling-api-base:python3.6 as production

COPY --from=build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages


COPY --from=build /dependencies /dependencies
COPY ./hseling_api_nauchpop /app/hseling_api_nauchpop
COPY ./hseling_api_nauchpop /dependencies/hseling_api_nauchpop
RUN pip install /dependencies

COPY ./app /app
