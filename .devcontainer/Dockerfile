FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*


ENV VENV_PATH="/workspaces/hitoq/backend/.venv"
ENV PATH="$VENV_PATH/bin:$PATH"

RUN curl -LsSf https://astral.sh/uv/0.7.2/install.sh | sh

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update -y && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    rm -rf /var/lib/apt/lists/*

CMD ["bash"]