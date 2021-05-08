import sqlite3 as sql
from typing import Dict

TTN_app_id_t = str

@dataclass
class ttn_app_t(Dict):

@dataclass
class device_t(Dict):
    device_id: str
    application_ids: dict
    dev_eui: str
    join_eui: str
    dev_addr: str


DB_filename = "database.db"

def insert_app(app_id: TTN_app_id_t):
    """
    Funció que incerta l'aplicació a la base de dades si no aquesta no hi està.
    """
    sql_connection = sql.connect(DB_filename)
    sql_cursor = sql_connection.cursor()

    sql_cursor.execute(
        "SELECT application_id FROM applications WHERE application_id = '?'",
        (app_id,))

    if (sql_cursor.fetchone() == None):
        sql_cursor.execute(
            "INSERT INTO applications (application_id) VALUES ('?')",
            (app_id,))
        sql_cursor.commit()
    
    sql_connection.close()

    
def insert_device(dev_info: device_t):
    """
    - Funció que incerta el dispositiu a la base de dades si no existeix
    - NO comprova si l'aplicació està en la base de dades.
    - Rep com a paràmetre un diccionari amb el següent format: (device_t)
    
    {"device_id":"heltec-esp32-lora",
    "application_ids": 
        {
        "application_id":"tfg-enric-garcia"
	},
    "dev_eui":"00DEACB0C6ABB5D2",
    "join_eui":"70B3D57ED0040582",
    "dev_addr":"260BF65F"
    }

    """
    sql_connection = sql.connect(DB_filename)
    sql_cursor = sql_connection.cursor()


    sql_cursor.execute(
        "SELECT device_id FROM devices WHERE device_id = '?'",
        (dev_info["device_id"],))

    if (sql_cursor.fetchone() == None):
        sql_cursor.execute(
            "INSERT INTO devices (device_id, application_id, dev_eui, join_eui, dev_addr) VALUES ('?', '?', '?', '?', '?')", (
                dev_info["device_id"],
                dev_info["application_ids"]["application_id"],
                dev_info["dev_eui"],
                dev_info["join_eui"],
                dev_info["dev_addr"]
            ))
        sql_cursor.commit()
    
    sql_connection.close()
