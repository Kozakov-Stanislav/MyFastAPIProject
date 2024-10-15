from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# ����� �� �������� �� ����
DB_TYPE = "mysql+pymysql"  # ��� "mysql+mysqlconnector" ���� �� ������������� mysql-connector
DB_DRIVER = "pymysql"
USER = "root"
PASSWORD = "Stas_1996"
HOST = "localhost"  # ��� IP-������ ������ �������
PORT = "3306"  # ��� ����, ���� �� �������������
DATABASE = "myfastapiprojectd"

DATABASE_URL = f"{DB_TYPE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("ϳ��������� �� ���� ����� ������!")
except OperationalError as e:
    print("������� ���������� �� ���� �����:", e)
