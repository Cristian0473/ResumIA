from decouple import config

pw = config('POSTGRES_PASSWORD')
print("PWD leído:", repr(pw), "— longitud:", len(pw))



from decouple import config
import psycopg2

def obtener_conexion():
    return psycopg2.connect(
        host=config('POSTGRES_HOST'),
        port=config('POSTGRES_PORT'),
        user=config('POSTGRES_USER'),
        password=config('POSTGRES_PASSWORD'),
        database=config('POSTGRES_DB'),
        sslmode=config('POSTGRES_SSLMODE', default='require')
    )
