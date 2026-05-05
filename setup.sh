#!/bin/bash

# Basic usage : ./setup.sh

ENV_FILE=.env
if [ ! -f "${ENV_FILE}" ]; then
    cp ./config/.env.example .env

    echo "The env file ${ENV_FILE} has been created, please fill it"
    exit 1
fi

source $ENV_FILE

## Environments Setup
export INSTANCE_NAME="${USER//./-}-$(basename "$(pwd)")"

export APP_ENV="dev"

export APP_SCHEME="http"
export APP_HOST="localhost"
export APP_PORT="8080"

## Construct Docker Compose
# We pass the override variable without quotes here so Bash treats the -f and the path as separate tokens
docker compose -p "${INSTANCE_NAME}" --project-directory . -f ./config/docker-compose.yml -f ./config/docker-compose-dev-override.yml config > docker-compose.yml

# Sanitize absolute paths to relative paths
sed -i -e "s#$(pwd)#.#g" docker-compose.yml

echo "-------------------------------------------------------"
echo "INSTANCE READY: ${INSTANCE_NAME}"
echo "-------------------------------------------------------"
echo "APP URL:  ${APP_SCHEME}://${APP_HOST}:${APP_PORT}/api/iot/docs"
echo "-------------------------------------------------------"
echo "Config:   docker-compose.yml generated."
echo "Action:   Run 'docker compose up -d' to start."
echo "-------------------------------------------------------"
