FROM python:3.11-slim@sha256:a90e299af8a9cd6b59c4aaed2b024c78561476978244a1ab89742a4a5ac8c974

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG USE_BETA_PACKAGE_VERSION=false
RUN if [ "${USE_BETA_PACKAGE_VERSION}" = "true" ]; then \
    pip install --pre --upgrade --force-reinstall maoto-agent; \
    fi

COPY maoto-agent/ ./maoto-agent/
ARG USE_LOCAL_PACKAGE_VERSION=false
RUN if [ "${USE_LOCAL_PACKAGE_VERSION}" = "true" ]; then \
    # Otherwise, install the maoto-agent with a pretend version
    export SETUPTOOLS_SCM_PRETEND_VERSION=1000.0.0a0 && pip install ./maoto-agent; \
    fi

WORKDIR /app

COPY . .

EXPOSE 80

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENTRYPOINT ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:80"]