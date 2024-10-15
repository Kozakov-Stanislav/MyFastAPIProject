from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Змініть ці значення на ваші
DB_TYPE = "mysql+pymysql"  # або "mysql+mysqlconnector" якщо ви використовуєте mysql-connector
DB_DRIVER = "pymysql"
USER = "root"
PASSWORD = "Stas_1996"
HOST = "localhost"  # або IP-адреса вашого сервера
PORT = "3306"  # або порт, який ви використовуєте
DATABASE = "myfastapiprojectd"

DATABASE_URL = f"{DB_TYPE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Підключення до бази даних успішне!")
except OperationalError as e:
    print("Помилка підключення до бази даних:", e)
