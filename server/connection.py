import mysql.connector
import json

class InventoryDb:
    """
    Class for handling the connection to the Inventory Database.

    Connector credintials can be provided to the constructor,
    which include host, user, and password.
    """
    def __init__(self,
                host="mysqldb",
                user="root",
                password="p@ssw0rd1"):
        self.host = host
        self.user = user
        self.password = password
        self.connector = mysql.connector.connect(
                            host=self.host,
                            user=self.user,
                            password=self.password)
        self.cursor = self.connector.cursor()

    def db_init(self, dbName = "inventory"):
        """
        Initializes the connection to the inventory database.
        """
        self.cursor.execute("DROP DATABASE IF EXISTS inventory")
        self.cursor.execute("CREATE DATABASE inventory")
        self.cursor.close()

        self.connector = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=dbName
        )
        self.cursor = self.connector.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS widgets")
        self.cursor.execute("CREATE TABLE widgets (name VARCHAR(255), description VARCHAR(255))")

    def get_widgets(self):
        """
        Gets all the widgets in the database.
        *Must* have initialized database before by using db_init.
        """
        self.cursor.execute("SELECT * FROM widgets")

        row_headers=[x[0] for x in self.cursor.description] #this will extract row headers

        results = self.cursor.fetchall()
        json_data=[]
        for result in results:
            json_data.append(dict(zip(row_headers,result)))

        return json.dumps(json_data)    
    