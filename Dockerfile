FROM hseling/hseling-api-base:python3.6 as build

LABEL maintainer="Sergey Sobko <ssobko@hse.ru>"

RUN mkdir /dependencies
COPY ./requirements.txt /dependencies/requirements.txt
COPY ./setup.py /dependencies/setup.py
RUN pip install --upgrade pip
RUN pip install -r /dependencies/requirements.txt


FROM hseling/hseling-api-base:python3.6 as production

COPY --from=build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=build /dependencies /dependencies
WORKDIR /app/
RUN pip install /dependencies
COPY ./hseling_api_nauchpop /app/hseling_api_nauchpop
RUN apt-get update
RUN apt-get install git
RUN apt-get install -y -o Dpkg::Options::="--force-confold" --no-install-recommends build-essential cmake lua5.2


RUN cd /app/hseling_api_nauchpop/ner_module  && \
git clone 'https://github.com/yandex/tomita-parser.git' && \
cd tomita-parser/ && mkdir build && cd build  && \
cmake ../src/ -DCMAKE_BUILD_TYPE=Release && \
make -j2
RUN mv '/app/hseling_api_nauchpop/lib/'* /app/hseling_api_nauchpop/ner_module/tomita-parser/build/bin
COPY ./app /app