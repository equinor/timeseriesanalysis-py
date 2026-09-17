ARG UV_VARIANT=0.12.15
ARG UV_DIGEST=sha256:62f8c047d0a0e9ece6b53fc63df902585a67a47a7f318ddec4a37db586edc8e3

ARG PYTHON_VERSION=dev-3.13-trixie
ARG PYTHON_DIGEST=sha256:96f800df841eed2de083cd0edb7c60a6b7d5eae608f02962aefb7bc8511ce819

ARG DOTNET_SDK_VERSION=8.0-jammy
ARG DOTNET_SDK_DIGEST=sha256:df5158092e643bf6407f0e048b5f8bcc231d72f963454b3dfa1f514faa992006

FROM docker.io/astral/uv:${UV_VARIANT}@${UV_DIGEST} AS uv
FROM mcr.microsoft.com/dotnet/sdk:${DOTNET_SDK_VERSION}@${DOTNET_SDK_DIGEST} AS dotnet

FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}@${PYTHON_DIGEST}

COPY --from=uv /uv /uvx /bin
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet

ENV UV_LINK_MODE=copy \
	UV_COMPILE_BYTECODE=1 \
	DOTNET_ROOT=/usr/share/dotnet

RUN ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet

WORKDIR /workspaces
