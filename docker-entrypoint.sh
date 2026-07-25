#!/bin/sh
set -e

echo "Aguardando o banco de dados MySQL ficar disponivel..."
python <<'PY'
import os
import sys
import time
from urllib.parse import urlparse

import pymysql

url = urlparse(os.environ["DATABASE_URL"])

for tentativa in range(30):
    try:
        conn = pymysql.connect(
            host=url.hostname,
            user=url.username,
            password=url.password or "",
            port=url.port or 3306,
            connect_timeout=3,
        )
        conn.close()
        break
    except Exception as exc:
        print(f"  tentativa {tentativa + 1}/30: {exc}")
        time.sleep(2)
else:
    sys.exit("Nao foi possivel conectar ao MySQL a tempo.")
PY

echo "Garantindo schema do banco (criar_banco.py)..."
python criar_banco.py

echo "Iniciando aplicacao Flask..."
exec python rotas.py
