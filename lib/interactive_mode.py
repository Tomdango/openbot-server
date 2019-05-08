import sys
import signal


class InteractiveMode():
    def __init__(self, application):
        self.app = application
        self.stopping = False

    def start(self):
        self.cli()

    @staticmethod
    def print(text):
        print("{0}\n".format(text), end=" ")

    def cli(self):
        try:
            command = input()
            if command.lower() == "quit":
                self.stopping = True
                self.app.safe_exit()
            else:
                print("[CLI] Command not recognised")
            self.cli()
        except KeyboardInterrupt:
            self.app.safe_exit()
        except SystemExit:
            print("Bye!")
            if (not self.stopping):
                self.app.safe_exit()
        except:
            print("There was an exception whilst executing your command.")

    def net2_handler(self, command):
        command_length = len(command)
        if (command_length > 1):
            if (command[1] == "connect"):
                self.app.net2.connect()
            elif command[1] == "status":
                print("Connection Status: {0}".format(
                    self.app.net2.connection_status))

        else:
            print("[NET2]: Available Commands - status")
        self.cli()
