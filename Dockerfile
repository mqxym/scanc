FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . /src

RUN python -m pip install --upgrade pip wheel && \
    pip wheel --wheel-dir /wheels ".[tiktoken]"


FROM python:3.13-slim AS runtime

ARG SCANC_VERSION=unknown
LABEL org.opencontainers.image.title="scanc"
LABEL org.opencontainers.image.description="Fast, pure-Python codebase scanner that emits AI-ready Markdown/XML"
LABEL org.opencontainers.image.version="${SCANC_VERSION}"
LABEL org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY}"
LABEL org.opencontainers.image.licenses="MIT"

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system --gid 10001 app && \
    adduser  --system --uid 10001 --ingroup app --home /home/app app

WORKDIR /work

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels

VOLUME ["/work"]

USER app:app

ENTRYPOINT ["scanc"]