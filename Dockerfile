# Dockerfile, used to build into an easily-deployed image
# Source: https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0

# The builder image, used to build the virtual environment
FROM python:3.13-bookworm AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY README.md ./

RUN uv sync --no-dev

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.13-bookworm AS runtime

RUN useradd -ms /bin/bash uwsgi

# Make /data dir be owned by uwsgi

WORKDIR /home/uwsgi
USER uwsgi
RUN mkdir data

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY bnuuy_time ./bnuuy_time

COPY buns.json ./

COPY uwsgi.ini ./

EXPOSE 8000
EXPOSE 9000

ENTRYPOINT ["sleep", "infinity"]
