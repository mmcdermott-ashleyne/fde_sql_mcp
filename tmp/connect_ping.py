import os
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(src_path))

os.environ['SQL_SERVER_HOST'] = 'fde_sql_server'
os.environ['SQL_SERVER_DATABASE'] = 'master'

from fde_sql_mcp.clients.sql import get_sql_connection
from fde_sql_mcp.config import settings

print('Configured server:', settings.sql_server)
print('Configured database:', settings.sql_database)

conn = get_sql_connection(server=settings.sql_server, database=settings.sql_database)
with conn.get_connection() as conn_obj:
    cursor = conn_obj.cursor()
    cursor.execute('SELECT 1')
    print('Query result:', cursor.fetchone())
    cursor.close()

print('Ping succeeded, SQL Server responded to simple query.')
