# IOT API

IOT API to manage ESP-32 custom connected devices with Google Home tool

## To setup local env

```bash
# To generate local .env file and local docker-compose file (with self traefik RP)
./setup
```

Here are the commands to install your development environment :

```bash
# To install Python dependencies
uv sync --dev

# To initialize codebase linters
uv run pre-commit install

# To run codebase linters
uv run pre-commit run -a
```

## To manage local env instance

```bash
# To build docker images
docker compose build

# To start Drawio app server
docker compose up -d

# To restart Drawio app server with rebuild image to update changed files
docker compose up -d --build

# To shutdown Drawio app server
docker compose down

# To see Drawio service logs
docker compose logs -f api
```
