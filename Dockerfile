FROM hseling/hseling-api-base:python3.6 as build

LABEL maintainer="Sergey Sobko <ssobko@hse.ru>"

#RUN apt-get update
#RUN apt-get install git
#RUN apt-get --assume-yes install gcc cmake lua5.2 libstdc++-6-dev

RUN mkdir /dependencies
COPY ./requirements.txt /dependencies/requirements.txt
COPY ./setup.py /dependencies/setup.py
COPY ./hseling_api_nauchpop /dependencies/hseling_api_nauchpop
RUN pip install --upgrade pip
RUN pip install -r /dependencies/requirements.txt


RUN apt-get update
RUN apt-get --assume-yes install gcc cmake lua5.2 libstdc++-6-dev
RUN \
cd /dependencies/hseling_api_nauchpop/tomita-parser && mkdir build && cd build  && \
cmake ../src/ -DCMAKE_BUILD_TYPE=Release && \
make
RUN mv '/dependencies/hseling_api_nauchpop/lib/'* /dependencies/hseling_api_nauchpop/tomita-parser/build/bin

FROM hseling/hseling-api-base:python3.6 as production

COPY --from=build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages


COPY --from=build /dependencies /dependencies
COPY --from=build /dependencies/hseling_api_nauchpop /app/hseling_api_nauchpop
RUN pip install /dependencies

#RUN apt-get update
#RUN apt-get install git
#RUN apt-get --assume-yes install build-essential lua5.2 cmake2.8
#COPY ./lib /tomita-parser/build/bin
COPY ./app /app

#RUN apt-get update
#RUN apt-get --assume-yes install gcc cmake lua5.2 libstdc++-6-dev
#RUN \
#cd hseling_api_nauchpop/tomita-parser && mkdir build && cd build  && \
#cmake ../src/ -DCMAKE_BUILD_TYPE=Release && \
#make
#RUN mv '/app/hseling_api_nauchpop/lib/'* /app/hseling_api_nauchpop/tomita-parser/build/bin
#mv hseling_api_nauchpop/lib/* /tomita-parser/build/bin/
#mv /tomita/build/FactExtract/Parser/tomita-parser/tomita-parser /tomita/parser && \
#rm -rf /tomita/.git /tomita/src /tomita/build

#COPY ./lib /tomita-parser/build/bin
#COPY ./app /app

