FROM nlpub/tomita:latest

LABEL maintainer="Sergey Sobko <ssobko@hse.ru>"

RUN apt-get update && apt-get -y install inotify-tools

WORKDIR /tomita/static
COPY tomita/static /tomita/static

RUN cd /tomita && \
    mkdir -p in out pretty && \
    chmod a+x /tomita/static/tomita.sh

CMD "/bin/bash" "/tomita/static/tomita.sh"
