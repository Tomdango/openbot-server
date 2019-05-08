import os
import sys
from time import sleep
from threading import Thread
from Net2Scripting import net2xs
from dotenv import load_dotenv
from lib.interactive_mode import InteractiveMode
from lib.net2.wrapper import Net2Wrapper
from lib.webserver.webserver import Webserver
from lib.database.member_db import MemberDB
from smtpd import SMTPServer
from datetime import datetime


class Application():
    def __init__(self):
        # Load Environment Variables
        load_dotenv()

        operator_id = os.getenv("OPERATOR_ID")
        operator_pwd = os.getenv("OPERATOR_PWD")
        net2_server = os.getenv("NET2_SERVER")
        if not operator_id or not operator_pwd or not net2_server:
            print("Error: Invalid Config Supplied.")
            print("Required Env Variables:")
            print("\t- OPERATOR_ID")
            print("\t- OPERATOR_PWD")
            print("\t- OPERATOR_NET2_SERVER")
            sys.exit(1)

        self.CONFIG = (int(operator_id), str(operator_pwd), str(net2_server))

        self.threads = []
        # Initialise Net2 Connection
        self._MAX_TRIES = 5
        self._RETRY_LOOP = 0

    def start(self):
        # self.open_net2_connection()
        self.cli = InteractiveMode(self)
        self.net2 = Net2Wrapper(self)
        self.webserver = Webserver(self)
        self.member_db = MemberDB()
        self.webserver.start()

        self.cli.start()

    def safe_exit(self):
        self.webserver.stop()
        for value in self.threads:
            print(value)
        if (self.net2):
            self.net2.tear_down()
        sys.exit(0)

    def trigger_fallback_mode(self):
        wait_for_connect_thread = Thread(
            target=self._wait_for_connect, daemon=True)
        wait_for_connect_thread.start()
        self.threads.append(wait_for_connect_thread)

    def _wait_for_connect(self):

        has_connected = self._try_connection()
        if has_connected:
            return
        else:
            self.interactive_mode.print("No Connect")

    def _try_connection(self):
        (OPERATOR_ID, OPERATOR_PWD, NET2_SERVER) = self.CONFIG
        with net2xs.Net2XS(NET2_SERVER) as net2:
            try:
                net2.authenticate(OPERATOR_ID, OPERATOR_PWD)
                print("Successfully opened connection to Net2. Exiting Fallback Mode.")
                self.net2 = net2
                return True
            except net2xs.Net2XSException:
                return False


if __name__ == "__main__":
    app = Application()
    try:
        app.start()
    except KeyboardInterrupt:
        app.safe_exit()
        print("Bye")
        sys.exit()
