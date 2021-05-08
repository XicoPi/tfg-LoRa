import sys
import sqlite3 as sql
from typing import Dict
from dataclasses import dataclass

TTN_app_id_t = str
TTN_dev_id_t = str
@dataclass
class ttn_app_t(Dict):
    application_id: TTN_app_id_t

@dataclass
class device_t(Dict):
    device_id: TTN_dev_id_t
    application_ids: TTN_app_id_t
    dev_eui: str #[17]
    join_eui: str #[17]
    dev_addr: str #[25]

@dataclass
class uplink_msg_t(Dict):
    #msg_id_time: str
    #device_id: TTN_dev_id_t #Foreign key: not in received from TTN message
    received_at: str
    session_key_id: str
    f_port: int
    f_cnt: int
    frm_payload: str
    rx_metadata: list
    settings: dict
    decoded_payload: dict
    consumed_airtime: str #[32]
#    confirmed: bool



class TTN_database(object):
    
    def __init__(self, db_filename: str, sql_filename: str):
        self.db_filename = db_filename

        sql_file = open(sql_filename, "r")
        file_data = sql_file.read()
        sql_file.close()
        

        sql_connection = sql.connect(db_filename)
        sql_cursor = sql_connection.cursor()

        sql_cursor.executescript(file_data)
        sql_connection.commit()

        sql_connection.close()

    def insert_app(self, app_id: TTN_app_id_t):
        """
        Funció que incerta l'aplicació a la base de dades si no aquesta no hi està.
        """
        try:
            sql_connection = sql.connect(self.db_filename)
            sql_cursor = sql_connection.cursor()
            
            sql_cursor.execute(
                "SELECT application_id FROM applications WHERE application_id = (?)",
                (app_id,))
            
            if (sql_cursor.fetchone() == None):
                sql_cursor.execute(
                    "INSERT INTO applications (application_id) VALUES ( (?) )",
                    (app_id,))
                sql_connection.commit()

            
        except KeyboardInterrupt:
            sql_connection.close()
            sys.exit(0)
        sql_connection.close()

    
    def insert_device(self, dev_info: device_t):
        """
        - Insert the ttn device to the database if it does not exist.
        - Do not comprovate if the TTN Application is registered/inserted into the database.

        """
        try:
            sql_connection = sql.connect(self.db_filename)
            sql_cursor = sql_connection.cursor()

            sql_cursor.execute(
                "SELECT device_id FROM devices WHERE device_id = (?)",
                (dev_info["device_id"],))
        
            if (sql_cursor.fetchone() == None):
                sql_cursor.execute(
                    "INSERT INTO devices (device_id, application_id, dev_eui, join_eui, dev_addr) VALUES ((?), (?), (?), (?), (?))",
                    (
                        dev_info["device_id"],
                        dev_info["application_ids"]["application_id"],
                        dev_info["dev_eui"],
                        dev_info["join_eui"],
                        dev_info["dev_addr"]
                    ))
                sql_connection.commit()

        except KeyboardInterrupt:
            sql_connection.close()
            sys.exit(0)
        sql_connection.close()

    def insert_uplink_msg(self, message: uplink_msg_t, device_id: TTN_dev_id_t):
        """
        - 
        - Do not comprovate if the device is registered/inserted into the database.
        - Do not comprovate if the there is a message with the same timestamp(primary key) in the database.
        """
        try:
            sql_connection = sql.connect(self.db_filename)
            sql_cursor = sql_connection.cursor()
            if ("decoded_payload" in message.keys()):
                sql_cursor.execute(
                    "INSERT INTO uplink_messages (msg_id_time, device_id, session_key_id, f_port, f_cnt, frm_payload, rx_metadata, settings, consumed_airtime, decoded_payload) VALUES ( (?), (?), (?), (?), (?), (?), (?), (?), (?), (?) )",
                    (
                        message["received_at"],
                        device_id,
                        message["session_key_id"],
                        message["f_port"],
                        message["f_cnt"],
                        message["frm_payload"],
                        str(message["rx_metadata"]),
                        str(message["settings"]),
                        message["consumed_airtime"],
                        str(message["decoded_payload"])
                    ))
            else:
                sql_cursor.execute(
                    "INSERT INTO uplink_messages (msg_id_time, device_id, session_key_id, f_port, f_cnt, frm_payload, rx_metadata, settings, consumed_airtime) VALUES ( (?), (?), (?), (?), (?), (?), (?), (?), (?) )",
                    (
                        message["received_at"],
                        device_id,
                        message["session_key_id"],
                        message["f_port"],
                        message["f_cnt"],
                        message["frm_payload"],
                        str(message["rx_metadata"]),
                        str(message["settings"]),
                        message["consumed_airtime"]
                    ))

            sql_connection.commit()

        except KeyboardInterrupt:
            sql_connection.close()
            sys.exit(0)
        sql_connection.close()
