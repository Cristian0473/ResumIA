from decouple import config
import psycopg2
import os

def obtener_conexion():
    # ── LÍNEAS DE DEPURACIÓN ───────────────────────────────
    print("ENV  POSTGRES_PORT:", os.environ.get("POSTGRES_PORT"))
    print(".env POSTGRES_PORT:", repr(config("POSTGRES_PORT", default="NO")))
    # ───────────────────────────────────────────────────────

    return psycopg2.connect(
        host=config('POSTGRES_HOST'),
        port=config('POSTGRES_PORT'),          # leerá 23841 si todo está bien
        user=config('POSTGRES_USER'),
        password=config('POSTGRES_PASSWORD'),
        database=config('POSTGRES_DB'),
        sslmode=config('POSTGRES_SSLMODE', default='require')
    )
