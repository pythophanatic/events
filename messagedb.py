#!/usr/bin/env python3
# coding=utf-8
"""
This file contains classes for handling messages and organizing them in a SQLite database
"""
import sqlite3
import os
import datetime
import hashlib
from secrets import token_urlsafe


class MessageDB:
    """
    This class handles messages in a SQLite database
    During initialisation a db file will be created if not exists
    """

    def __init__(self, db_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'message.db')):
        """
        Constructor for the MessageDB object

        :param db_file: Location of the sqlite db-file. Must be an absolute path.
        """
        self.BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        self.db_file = db_file
        self.__check_db_file()
        self.__init_db()

    def __init_db(self):
        """
        Checks if the sqlite db file exists and has a valid data-structure.

        :return: None
        """
        default_sql = os.path.join(self.BASE_DIR, 'db_scheme.sql')
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        with open(default_sql) as f:
            c.executescript(f.read())
        db_connection.commit()
        db_connection.close()
        return None

    def __check_db_file(self):
        """
        Checks if db_file exists, otherwise an empty file will be created
        :return: None
        """
        if not os.path.isfile(self.db_file):
            open(self.db_file, 'a').close()

    @staticmethod
    def __generate_token():
        return token_urlsafe(18)

    @staticmethod
    def __now():
        """
        :return: Returns the actual time in a special string format
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    @staticmethod
    def __hash_token(token):
        """
        :param token: token to hash to
        :return: SHA3_512 hashed token
        """
        m = hashlib.sha3_512()
        for i in range(100000):
            m.update(token.encode())
        return m.hexdigest()

    def __user_exists(self, username):
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        c.execute("SELECT id FROM user u WHERE u.name = ?", (username,))
        queried_user = c.fetchone()
        db_connection.close()
        if not queried_user:
            user_exists = None
        else:
            user_exists = queried_user[0]
        db_connection.close()
        return user_exists

    def __get_user_by_token(self, token):
        hashed_token = self.__hash_token(token)
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.execute("SELECT id FROM user u WHERE u.token = ?", (hashed_token,))
        query = c.fetchone()
        db_connection.close()
        if query:
            return query[0]
        else:
            return None

    def __get_username(self, user_id):
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.execute("SELECT name FROM user u WHERE u.id = ?", (user_id,))
        query = c.fetchone()
        db_connection.close()
        if query:
            return query[0]
        else:
            return None

    def __check_token(self, token, username):
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        c.execute("SELECT token FROM user u WHERE u.name = ?", (username,))
        hashed_token = c.fetchone()[0]
        db_connection.close()
        if hashed_token == self.__hash_token(token):
            return True
        else:
            return False

    def __user_activated(self, user_id):
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        c.execute("SELECT activated FROM user u WHERE u.id = ?", (user_id,))
        user_activated = c.fetchone()[0]
        db_connection.close()
        return user_activated

    def create_user(self, username):
        """
        Creates a new user for the message_db
        :param username: new username
        :return: Returns the new generated token, if username was already in use, return false
        """
        token = self.__generate_token()
        hashed_token = self.__hash_token(token)
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        user_activated = True
        data = (username, hashed_token, self.__now(), user_activated)
        try:
            c.execute("INSERT INTO user (name, token, created, activated) VALUES (?, ?, ?, ?)", data)
        except sqlite3.IntegrityError:
            return False
        db_connection.commit()
        db_connection.close()
        return token

    def new_message(self, data):
        """
        Saves a new message to the message_db
        :param data: A dictionary with the keys topic, details, priority
        :return: True is message was processed properly, else function returns false, then a status message and
        the id of the new message is returned
        """
        topic = data['topic']
        details = data.get('details', None)
        priority = data['priority']
        token = data['token']
        user_id = self.__get_user_by_token(token)
        if not user_id:
            return False, "Unknown token!", None
        if not self.__user_activated(user_id):
            return False, "User not activated!", None
        archived = False
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        data = (user_id, self.__now(), topic, priority, details, archived)
        c.execute("INSERT INTO messages "
                  "(user_id, date, topic, priority, details, archived) "
                  "VALUES (?, ?, ?, ?, ?, ?)", data)
        c.execute("select last_insert_rowid();")
        message_id = c.fetchone()[0]
        db_connection.commit()
        db_connection.close()
        return True, "new message processed successfully", message_id

    def messages_by_token(self, token):
        """
        Queries all unarchived messages from the database
        :return: A list of dicts with queried messages
        """
        user_id = self.__get_user_by_token(token)
        if user_id and self.__user_activated(user_id):
            if self.__user_activated(user_id):
                archived = False
                db_connection = sqlite3.connect(self.db_file)
                c = db_connection.cursor()
                c.execute("SELECT * FROM messages m WHERE m.archived = ? AND m.user_id = ?", (archived, user_id))
                messages = []
                for message in c.fetchall():
                    messages.append({'id': message[0],
                                     'user_id': user_id,
                                     'date': message[2],
                                     'topic': message[3],
                                     'priority': message[4],
                                     'details': message[5],
                                     'archived': message[6]})
                db_connection.close()
                return True, "Messages were queried!", messages
            else:
                return False, "User not active!", None
        else:
            return False, "Unknown token!", None
