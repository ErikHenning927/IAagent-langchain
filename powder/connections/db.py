import pyodbc


def db_local():
    server = 'localhost,1433'
    database = 'master' 
    username = 'sa'
    password = 'Admin123!'

    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    try:
        conn = pyodbc.connect(connection_string)
        print("Conexão estabelecida com sucesso!")

        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")