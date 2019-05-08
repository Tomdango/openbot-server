from Net2Scripting.net2xs import Net2XS, Net2XSException, conversions
from threading import Thread
from time import sleep
import os
import json
import pickle
import sys


class Net2Wrapper():
    DISCONNECTED = "Disconnected"
    CONNECTED = "Connected"
    CONNECTING = "Connecting"

    def __init__(self, application):
        self.app = application
        self.connected = False
        self.connection_status = "Disconnected"
        self._RETRY_LOOP = 0
        self._MAX_TRIES = 1
        self.api = False
        self.keep_thread_alive = True
        self.connect_in_background = True
        self.background_connect()

    def connect(self, background=True):
        """
            Wrapper for the _attempt_connection function
        """
        (OPERATOR_ID, OPERATOR_PWD, NET2_SERVER) = self.app.CONFIG
        self.connection_status = self.CONNECTING
        self.connected = False
        self._attempt_connection(NET2_SERVER, OPERATOR_ID, OPERATOR_PWD)

    def _attempt_connection(self, net2_server, uid, pwd):
        """
            Attempt connection to the Net2 Server.
            Returns a tuple (connected, net2)
        """
        print("[NET2] Attempting to establish connection to Net2 Server on {0} (Operator ID: {1})".format(
            net2_server, uid))
        with Net2XS(net2_server) as net2:
            try:
                net2.authenticate(uid, pwd)
                print("[NET2] Connection Established.")
                self.connection_status = self.CONNECTED
                self.api = net2
                self.connected = True
                self._connect_thread_complete()
            except Net2XSException as exception:
                print("[NET2] Connection Failed.")
                print("[NET2] {0}".format(exception))
                self.connection_status = self.DISCONNECTED
                self.connected = False
                self.api = False
                self._connect_thread_complete()
            except Exception as exception:
                print("[NET2] An unhandled exception occured during connection.")
                print("[NET2] {0}".format(exception))
                self.connection_status = self.DISCONNECTED
                self.connected = False
                self.api = False
                self._connect_thread_complete()

    def _connect_thread_complete(self):
        if not self.connected:
            sleep(10)
            self.background_connect()
        else:
            self.keep_thread_alive = True
            while self.keep_thread_alive:
                try:
                    sleep(0.25)
                except Exception as e:
                    print("[NET2] Exception in Net2 Thread")
                    print("[NET2] {0}".format(e))

    def user_has_access(self, username):
        # Don't touch. You might break it.
        (first_name, last_name) = username.split(" ")
        user_id = self.api.get_user_id_by_name((first_name, last_name))
        raw_user_record = self.api.get_user_record(user_id)
        user_record = conversions.user_view_to_py(raw_user_record)
        if user_record.get("access_level_id") == 1:
            return (True, user_record)
        else:
            return (False, False)

    def background_connect(self):
        self.connect_thread = Thread(
            target=self.connect,
            daemon=True,
            args=(True,))
        self.connect_thread.start()

    def is_connected(self):
        return self.connected

    def tear_down(self):
        if self.api:
            print("[NET2] Killing Net2 Daemon")
            try:
                self.api.dispose()
                print("[NET2] Killed Net2 Daemon")
            except:
                print("[NET2] Error whilst killing Net2 Daemon")
        else:
            print("[NET2] Net2 Daemon not initialised - Nothing to kill")
        self.keep_thread_alive = False
