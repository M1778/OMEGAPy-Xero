# Imports
from configparser import ConfigParser
import sqlite3
import datetime
import secrets
import string

# Read config
config = ConfigParser()
config.read("sql.cfg")
sqlpath = config['sqlconfig']['sqlpath']


class ManageDatabase:
    def __init__(self, name: str):
        self.name = name
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def reconnect(self, name: str):
        self.name = name
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()

    def query(self, sqlquery):
        return self.cursor.execute(sqlquery)

    def query_f(self, sqlquery, data):
        return self.cursor.executemany(sqlquery, data)

    def commit(self):
        return self.connection.commit()

    def fetchall(self, sqlquery):
        return self.cursor.execute(sqlquery).fetchall()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()


MD = ManageDatabase(sqlpath)

initial = """
CREATE TABLE IF NOT EXISTS users(
    username TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL,
    registerdate TEXT NOT NULL,
    accesslvl INTEGER DEFAULT 1
);
"""

initial2 = """
CREATE TABLE IF NOT EXISTS messages(
    messageid INTEGER,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    PRIMARY KEY (messageid AUTOINCREMENT)
);"""

MD.query(initial)
MD.query(initial2)
MD.commit()

adminexists = False
for i in MD.fetchall("SELECT username FROM users"):
    if i[0] == "admin":
        adminexists = True

if adminexists is False:
    alphabet = string.ascii_letters + string.digits
    admin_password = ''.join(secrets.choice(alphabet) for _ in range(20))
    MD.query_f(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        [("admin", admin_password, str(datetime.datetime.now(datetime.timezone.utc)), 3)]
    )
    MD.commit()
    print("=" * 60)
    print("WARNING: First run detected. Admin account created.")
    print(f"  Username: admin")
    print(f"  Password: {admin_password}")
    print("Please save this password securely. It will not be shown again.")
    print("=" * 60)


def reset_messages():
    MD.query("DROP TABLE messages")
    MD.commit()


def add_message(message_role, message_content):
    MD.query_f("INSERT INTO messages (role,content) VALUES (?, ?)", [(message_role, message_content)])
    MD.commit()


def get_messages():
    return MD.fetchall("SELECT * FROM messages")
