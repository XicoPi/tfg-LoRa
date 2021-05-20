import json

ttn_mqtt_auth_t = {
    "username": str,
    "password": str
}

db_auth_t = {
    "host": str,
    "username": str,
    "password": str,
    "database": str
}

credentials_set_t = {
    "ttn_auth": ttn_mqtt_auth_t,
    "db_auth": db_auth_t
}

class Credentials_Manager(object):
    def __init__(self,filename: str , reset: bool):

        #filename = input("Put the name of the credential file: ")
        self.filename = filename
        if (reset == True):
            credentials = self._get_new_credentials()

        with open(filename, "r") as credential_file:
            credentials = json.loads(credential_file.read())
#except FileNotFoundError:
#            credentials = self._get_new_credentials()

        
        self.ttn_auth = credentials["ttn_auth"]
        self.db_auth = credentials["db_auth"]
        self.filename = filename

    def _get_new_credentials(self) -> credential_set_t:

        print("The Things Network Authentication\n")
        ttn_auth_credentials = {
            "username": input("Put TTN Username: "),
            "password": input("Put TTN Password: ")
        }
        print("\nMySQL Database Authentication\n")
        mysql_db_credentials = {
            "host": input("Put DB hostname: "),
            "username": input("Put DB username: "),
            "password": input("Put DB password: "),
            "database": input("Put DB database name: ")
        }
        
        with open(self.filename, "w") as credentials_file:
            credentials_data = {
                "ttn_auth": ttn_auth_credentials,
                "db_auth": mysql_db_credentials
            }

            file_write_content = json.dumps(credentials_data)
            credentials_file.write(file_write_content)
        return credentials_data
