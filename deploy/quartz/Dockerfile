# syntax=docker/dockerfile:1.7
FROM --platform=$BUILDPLATFORM node:22-bookworm-slim@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d AS quartz-deps
ARG QUARTZ_COMMIT=d25a6eabf96751ffca56f8a8139272def7a65041
ARG QUARTZ_SHA256=40c17cdb5e6bbd39850171c9d83acd74dcae9266cb6fba17bc41607682fb8ce7
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /quartz
ADD --checksum=sha256:${QUARTZ_SHA256} \
    https://github.com/jackyzha0/quartz/archive/${QUARTZ_COMMIT}.tar.gz /tmp/quartz.tar.gz
RUN tar -xzf /tmp/quartz.tar.gz --strip-components=1 -C /quartz \
    && rm -f /tmp/quartz.tar.gz \
    && npm ci --no-audit --no-fund

FROM --platform=$BUILDPLATFORM quartz-deps AS builder
WORKDIR /repo
COPY . /repo
RUN cp /repo/deploy/quartz/quartz.config.ts /quartz/quartz.config.ts \
    && cp /repo/deploy/quartz/quartz.layout.ts /quartz/quartz.layout.ts \
    && python3 /repo/deploy/quartz/prepare_content.py \
        --repo-root /repo \
        --output-dir /quartz/content \
        --layout-file /quartz/quartz.layout.ts \
    && cd /quartz \
    && node ./quartz/bootstrap-cli.mjs build

FROM nginxinc/nginx-unprivileged:1.27-alpine@sha256:65e3e85dbaed8ba248841d9d58a899b6197106c23cb0ff1a132b7bfe0547e4c0
COPY deploy/quartz/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /quartz/public /usr/share/nginx/html
USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/health || exit 1
