#!/usr/bin/env bash
set -euo pipefail

# ===== CONFIG =====
WEBAPP_CONTAINER="2_network_webapp"
KNOCK_CONTAINER="2_network_port_knocking"
TARGET_IP="172.20.0.40"
SEQUENCE="1234,5678,9012"
PROTECTED_PORT=2222
NC_TIMEOUT=2  
LOCAL_PORT_KNOCKING_DIR="/root/csce413_assignment2/port_knocking"  
CONTAINER_PORT_KNOCKING_DIR="/tmp/port_knocking"
# ==================

echo "[*] Restarting knock server container to clear old state"
docker restart ${KNOCK_CONTAINER}

echo "[*] Copying port_knocking code into the webapp container"
docker cp "${LOCAL_PORT_KNOCKING_DIR}/." "${WEBAPP_CONTAINER}:${CONTAINER_PORT_KNOCKING_DIR}"

echo "[*] Ensuring netcat is installed in the webapp container"
docker exec "${WEBAPP_CONTAINER}" sh -c "apt-get update && apt-get install -y netcat-openbsd"

echo "[*] Starting knock server inside ${KNOCK_CONTAINER}"
docker exec -d ${KNOCK_CONTAINER} python3 /tmp/port_knocking/knock_server.py

sleep 2

echo "[*] Starting protected port listener on ${PROTECTED_PORT}"
docker exec -d ${KNOCK_CONTAINER} nc -lkp ${PROTECTED_PORT} >/dev/null

sleep 1

echo "[1/3] Attempting protected port BEFORE knocking (should fail)"
docker exec ${WEBAPP_CONTAINER} \
  nc -z -v -w ${NC_TIMEOUT} ${TARGET_IP} ${PROTECTED_PORT} || echo "[✓] As expected, port is closed"

echo "[2/3] Sending knock sequence from webapp container"
docker exec ${WEBAPP_CONTAINER} \
  python3 ${CONTAINER_PORT_KNOCKING_DIR}/knock_client.py \
    --target ${TARGET_IP} \
    --sequence ${SEQUENCE} \
    --check

sleep 1

echo "[3/3] Attempting protected port AFTER knocking (should succeed)"
docker exec ${WEBAPP_CONTAINER} \
  nc -z -v -w ${NC_TIMEOUT} ${TARGET_IP} ${PROTECTED_PORT} && echo "[✓] Port is open after knocking" || echo "[✗] Port still closed"

echo "[✓] Port knocking demo complete"
