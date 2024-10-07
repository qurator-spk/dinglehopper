ARG DOCKER_BASE_IMAGE
FROM $DOCKER_BASE_IMAGE
ARG VCS_REF
ARG BUILD_DATE
LABEL \
LABEL \
    maintainer="https://github.com/qurator-spk/dinglehopper/issues" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/qurator-spk/dinglehopper" \
    org.label-schema.build-date=$BUILD_DATE
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/qurator-spk/dinglehopper" \
    org.label-schema.build-date=$BUILD_DATE

WORKDIR /build/dinglehopper
COPY pyproject.toml .
COPY src/dinglehopper/ocrd-tool.json .
COPY src ./src
COPY requirements.txt .
COPY README.md .
COPY Makefile .
RUN make install
RUN rm -rf /build/dinglehopper

WORKDIR /data
VOLUME ["/data"]
