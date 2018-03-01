#!/usr/bin/env python3
# coding=utf-8
"""
This class offers helper classes fot the api server
"""
import json
from messagedb import MessageDB


class Response:
    """
    This class gives a standard response object. Responses are given back from the class as json-strings
    """
    def __init__(self):
        self.__data = {
            'status': '',
            'message': '',
        }

    def __init_data(self):
        self.__data['data'] = {}

    def __set_message(self, message):
        self.__data['message'] = message

    def __set_status(self, status):
        self.__data['status'] = status

    def append_data(self, key, value):
        """
        Append data to te data section of the response
        :param key: Key to append
        :param value: Value to append
        :return: None
        """
        if not self.__data.get('data', None):
            self.__init_data()
        self.__data['data'][key] = value

    def fail(self, message="A failure occurred"):
        """
        Creates a standard fail response
        :param message: Describes the failure happened
        :return: fail response data
        """
        self.__set_status('fail')
        self.__set_message(message)
        return json.dumps(self.__data)

    def ok(self, message="request processed properly"):
        """
        Creates a standard ok response
        :param message: Describes the failure happened
        :return: ok response data
        """
        self.__set_status('ok')
        self.__set_message(message)
        return json.dumps(self.__data)


class ApiFunctions:
    """
    Objects of this class deliver the actual functions of the message_db api service
    """

    def process_message(self, req):
        """
        Process an incoming message with the request var fro outer scope
        :return: None
        """
        response = Response()
        data = {}
        needed_data = ['topic', 'priority', 'token']
        processed = None
        message_id = None
        if req.get_data():
            data = json.loads(req.get_data().decode())
        if self.__all_keys_in_data(needed_data, data):
            db = MessageDB()
            processed, message, message_id = db.new_message(data)
        else:
            message = "Missing argument(s)!"
        if processed:
            response.append_data('message_id', message_id)
            return response.ok(message)
        return response.fail(message)

    @staticmethod
    def __all_keys_in_data(key_list, data):
        """
        Checks if there is a value for every given key in data

        :return: True if all keys were found in data or false if not
        """
        for key in key_list:
            if key in data:
                pass
            else:
                return False
        return True
