from unittest import TestCase
import os
from messagedb import MessageDB
import sqlite3


class TestMessageDB(TestCase):

    def __query_user_by_name(self, username):
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        c.execute("SELECT id FROM user u WHERE u.name = ?", (username,))
        user_id = c.fetchone()[0]
        return user_id

    def setUp(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        self.db_file = os.path.join(base_dir, 'test.db')
        if os.path.isfile(self.db_file):
            os.remove(self.db_file)
        self.db = MessageDB(db_file=self.db_file)
        self.username = "steve"
        self.token = self.db.create_user(self.username)
        self.start_user_id = 1
        default_sql = os.path.join(base_dir, 'test_messages.sql')
        db_connection = sqlite3.connect(self.db_file)
        c = db_connection.cursor()
        with open(default_sql) as f:
            content = f.read()
            self.start_message_id= len(content.splitlines())
            c.executescript(content)
        db_connection.commit()
        db_connection.close()

    def tearDown(self):
        if os.path.isfile(self.db_file):
            os.remove(self.db_file)

    def test_new_message(self):
        self.assertNotEqual(self.token, False, "No token was generated!")
        data = {'topic': 'new mail', 'token': self.token, 'priority': 3}
        success, message, message_id = self.db.new_message(data)
        self.assertTrue(success)
        self.assertEqual("new message processed successfully", message)
        self.assertEqual(message_id, self.start_message_id + 1, "First msg_id not " + str(self.start_message_id + 1))
        status, message, msg_dump = self.db.messages_by_token(self.token)
        msg_dump = msg_dump[-1]
        self.assertTrue(status, "Processing message failed")
        self.assertEqual("Messages were queried!", message)
        self.assertEqual(msg_dump['topic'], data['topic'], "Wrong topic in db")
        self.assertEqual(msg_dump['priority'], data['priority'], "Wrong priority in DB")
        self.assertEqual(msg_dump['details'], None, "Wrong details in db")

    def test_create_user(self):
        token = self.db.create_user(self.username)
        self.assertEqual(token, False, "User already exists, create_user should return False!")
        username = "jules"
        token = self.db.create_user(username)
        expected_token_length = 24
        self.assertEqual(len(token), expected_token_length, "Token doesn't have expected length")
        expected_user_id = self.start_user_id + 1
        user_id = self.__query_user_by_name(username)
        self.assertEqual(expected_user_id, user_id, "Created User " + username + " has not expected id")
