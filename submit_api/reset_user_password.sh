#!/bin/bash
# Usage: ./reset_user_password.sh <email> <new_password>

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <email> <new_password>"
    exit 1
fi

EMAIL="$1"
NEW_PASSWORD="$2"

docker compose exec fastapi-app python reset_password_admin.py "$EMAIL" "$NEW_PASSWORD"
