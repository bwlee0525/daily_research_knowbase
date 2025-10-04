FROM mcr.microsoft.com/devcontainers/python:3.11
RUN apt-get update && apt-get install -y curl gnupg &&     curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&     apt-get install -y nodejs &&     rm -rf /var/lib/apt/lists/*
WORKDIR /workspaces
