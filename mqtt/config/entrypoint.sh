#!/bin/sh
set -e

# Path to the password file
PASSWD_FILE="/mosquitto/config/passwords.txt"

# 1. Create the file if it doesn't exist
touch $PASSWD_FILE

chown root:root $PASSWD_FILE
chmod 0700 $PASSWD_FILE

# 2. Add the users
# Syntax: mosquitto_passwd -b <file> <username> <password>
# The -b flag enables batch mode (no interactive prompt)
mosquitto_passwd -b $PASSWD_FILE $PUBLISHER_USERNAME $PUBLISHER_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $SUBSCRIBER_1_USERNAME $SUBSCRIBER_1_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $SUBSCRIBER_2_USERNAME $SUBSCRIBER_2_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $SUBSCRIBER_3_USERNAME $SUBSCRIBER_3_PASSWORD

# 3. Execute the original Mosquitto image entrypoint with the passed arguments (starts the broker)
exec /docker-entrypoint.sh "$@"