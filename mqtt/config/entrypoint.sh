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
mosquitto_passwd -b $PASSWD_FILE $IOT_API_USERNAME $IOT_API_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $DEVICE_1_USERNAME $DEVICE_1_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $DEVICE_2_USERNAME $DEVICE_2_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $DEVICE_3_USERNAME $DEVICE_3_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $DEVICE_4_USERNAME $DEVICE_4_PASSWORD
mosquitto_passwd -b $PASSWD_FILE $DEVICE_5_USERNAME $DEVICE_5_PASSWORD

# 3. Execute the original Mosquitto image entrypoint with the passed arguments (starts the broker)
exec /docker-entrypoint.sh "$@"
