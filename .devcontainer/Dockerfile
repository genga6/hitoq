FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    git \
    curl \
    gnupg \
    software-properties-common \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list

RUN apt-get update && apt-get install -y terraform

ENV VENV_PATH="/workspaces/hitoq/backend/.venv"
ENV PATH="$VENV_PATH/bin:$PATH"

RUN curl -LsSf https://astral.sh/uv/0.7.2/install.sh | sh

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update -y && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    rm -rf /var/lib/apt/lists/*

CMD ["bash"]
