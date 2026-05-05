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

CERTS_DIR="./mqtt/certs"
mkdir -p "$CERTS_DIR"

if [ ! -f "$CERTS_DIR/server.crt" ] || [ ! -f "$CERTS_DIR/ca.crt" ]; then
    echo "-------------------------------------------------------"
    echo "MQTT certificates not found."
    echo "Generate self-signed certificates..."
    echo "-------------------------------------------------------"

    # 1. Générer la clé et le certificat de l'Autorité de Certification (CA)
    # -nodes évite de mettre un mot de passe sur la clé pour automatiser le processus
    openssl req -new -x509 -days 3650 -extensions v3_ca \
        -keyout "$CERTS_DIR/ca.key" \
        -out "$CERTS_DIR/ca.crt" \
        -subj "/C=FR/ST=Region/L=City/O=IoT_Project/CN=IoT_Root_CA" -nodes

    # 2. Générer la clé privée du serveur MQTT
    openssl genrsa -out "$CERTS_DIR/server.key" 2048

    # 3. Créer la demande de signature de certificat (CSR)
    # Le Common Name (CN) correspond au domaine défini dans ton infrastructure
    openssl req -new \
        -out "$CERTS_DIR/server.csr" \
        -key "$CERTS_DIR/server.key" \
        -subj "/C=FR/ST=Region/L=City/O=IoT_Project/CN=${APP_HOST}"

    # 4. Signer le certificat du serveur avec notre propre CA
    openssl x509 -req \
        -in "$CERTS_DIR/server.csr" \
        -CA "$CERTS_DIR/ca.crt" \
        -CAkey "$CERTS_DIR/ca.key" \
        -CAcreateserial \
        -out "$CERTS_DIR/server.crt" \
        -days 3650

    # 5. Nettoyage et permissions
    rm "$CERTS_DIR/server.csr" "$CERTS_DIR/ca.srl"

    # On s'assure que le conteneur Mosquitto pourra lire ces fichiers
    chmod 644 "$CERTS_DIR/ca.crt" "$CERTS_DIR/server.crt" "$CERTS_DIR/server.key"
fi

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
