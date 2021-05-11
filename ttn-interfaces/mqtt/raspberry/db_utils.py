import sys
import mysql.connector as sql
import contextlib

from typing import Dict
from dataclasses import dataclass
from datetime import datetime

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

@dataclass
class msg_payload_t(Dict):
    received_at: str
    battery: int
    event: str #[16]
    light: int
    temperature: float


@contextlib.contextmanager
def db_connection_handler(host: str, user: str, password: str, database: str):
    try:
        sql_connection = sql.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database)
        yield sql_connection

    finally:
        sql_connection.close()


class TTN_database:
    
    def __init__(self, host: str, user: str, password: str, database:str):
        self.host = host
        self.user = user
        self._password = password
        self.database = database


    def _insert_node_msg_payload(self, payload: msg_payload_t, received_at: str):

        with db_connection_handler(host=self.host,
                                   user=self.user,
                                   password=self._password,
                                   database=self.database) as sql_connection:
            #sql_connection = sql.connect(host=self.host,
            #                             

            sql_cursor = sql_connection.cursor()

            sql_cursor.execute(
                "INSERT INTO node_decoded_payloads (msg_id_time, battery, event, light, temperature) VALUES ( %s, %s, %s, %s, %s )",
                (
                    datetime.strptime(received_at[:-4], "%Y-%m-%dT%H:%M:%S.%f"),
                    payload["battery"],
                    payload["event"],
                    payload["light"],
                    payload["temperature"]
                ))
            sql_connection.commit()

        #finally:
        #    sql_connection.close()
        
    def insert_app(self, app_id: TTN_app_id_t):
        """
        Funció que incerta l'aplicació a la base de dades si no aquesta no hi està.
        """
        with db_connection_handler(host=self.host,
                                   user=self.user,
                                   password=self._password,
                                   database=self.database) as sql_connection:

            sql_cursor = sql_connection.cursor()
            
            sql_cursor.execute(
                "SELECT application_id FROM applications WHERE application_id = %s",
                (app_id,))
            
            if (sql_cursor.fetchone() == None):
                sql_cursor.execute(
                    "INSERT INTO applications (application_id) VALUES ( %s )",
                    (app_id,))
                sql_connection.commit()

    
    def insert_device(self, dev_info: device_t):
        """
        - Insert the ttn device to the database if it does not exist.
        - Do not comprovate if the TTN Application is registered/inserted into the database.

        """
        with db_connection_handler(host=self.host,
                                   user=self.user,
                                   password=self._password,
                                   database=self.database) as sql_connection:

            sql_cursor = sql_connection.cursor()

            sql_cursor.execute(
                "SELECT device_id FROM devices WHERE device_id = %s",
                (dev_info["device_id"],))
        
            if (sql_cursor.fetchone() == None):
                sql_cursor.execute(
                    "INSERT INTO devices (device_id, application_id, dev_eui, join_eui, dev_addr) VALUES (%s, %s, %s, %s, %s)",
                    (
                        dev_info["device_id"],
                        dev_info["application_ids"]["application_id"],
                        dev_info["dev_eui"],
                        dev_info["join_eui"],
                        dev_info["dev_addr"]
                    ))
                sql_connection.commit()

    def insert_uplink_msg(self, message: uplink_msg_t, device_id: TTN_dev_id_t):
        """
        - Do not comprovate if the device is registered/inserted into the database.
        - Do not comprovate if the there is a message with the same timestamp(primary key) in the database.
        """
        with db_connection_handler(host=self.host,
                                   user=self.user,
                                   password=self._password,
                                   database=self.database) as sql_connection:

            sql_cursor = sql_connection.cursor()
            with contextlib.suppress(KeyError):
                sql_cursor.execute(
                    "INSERT INTO uplink_messages (msg_id_time, device_id, session_key_id, f_port, f_cnt, frm_payload, rx_metadata, settings, consumed_airtime) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        datetime.strptime(message["received_at"][:-4], "%Y-%m-%dT%H:%M:%S.%f"),
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

        if ("decoded_payload" in message.keys()):
            self._insert_node_msg_payload(message["decoded_payload"], message["received_at"])

    
