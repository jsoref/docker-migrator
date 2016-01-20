FROM alpine:3.2

RUN (apk add --update bash curl jq wget &&\
  rm -rf /var/cache/apk/*)

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

### use docker-1.6.2; upgrading will break password decryption
RUN (wget "https://get.docker.com/builds/Linux/x86_64/docker-1.6.2" -O /usr/bin/docker &&\
  chmod +x /usr/bin/docker)
COPY migrator.sh /usr/local/bin/migrator.sh

RUN pip install requests
ADD compare_registries.py /usr/local/bin/compare_registries.py
CMD ["/usr/local/bin/migrator.sh"]
