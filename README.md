![CI/CD Status](https://github.com/AureProd/iot-api/actions/workflows/main.yml/badge.svg)

# 🌐 IoT API Server

An IoT API designed to manage custom ESP-32 connected devices using Google Home integration.

## 💻 Local Environment Setup

Run the automated setup script to generate your local environment variables (`.env`) and a customized Docker Compose file (which includes a Traefik reverse proxy):

```bash
# To generate local .env file and local docker-compose file (with self traefik RP)
./setup
```

Next, install your Python development environment and dependencies :

```bash
# To install Python dependencies
uv sync --dev
```

Initialize and run the codebase linters to maintain code quality :

```bash
# To initialize codebase linters
uv run pre-commit install

# To run codebase linters
uv run pre-commit run -a
```

## 🐳 Docker Container Management

Use the following commands to control your local API instance using Docker Compose:

```bash
# To build Docker images
docker compose build

# To start API server in the background
docker compose up -d

# To rebuild and apply recent file changes
docker compose up -d --build

# To stop and shut down the API server
docker compose down

# To see and follow API service logs in real-time
docker compose logs -f api
```
