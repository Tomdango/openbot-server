from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from lib.constants.message_types import BroadcastTypes
import cherrypy
import json
from cherrypy.process import plugins
from ws4py.messaging import TextMessage
bus = cherrypy.engine


class OpenBotWebSocketHandler(WebSocket):
    def set_variable(self, key, value):
        if "variables" not in self.__dict__.values():
            self.variables = {}

        self.variables["{0}".format(key)] = value

    def get_variable(self, key):
        if "variables" not in self.__dict__.values():
            self.variables = {}
        try:
            return self.variables.get(key)
        except:
            return False

    def received_message(self, m):
        message = json.loads(str(m))
        if "apiKey" not in message or "action" not in message:
            print("Recieved Message without apiKey or action")
            pass
        else:
            action = message.get("action")
            if action == "connection":
                response = json.dumps({
                    "messageType": "connection",
                    "messageData": {
                        # pylint: disable=no-member
                        "serverVersion": bus.serverVersion,
                        "net2ServerConnection": bus.net2.connection_status
                        # pylint: disable=no-member
                    }
                })
                self.send(response)


class OpenBotWebSocketPlugin(WebSocketPlugin):
    def __init__(self, bus):
        WebSocketPlugin.__init__(self, bus)

    def broadcast_changes(self):
        self.bus.publish("websocket-broadcast", "{}")

    def net2_disconnected(self):
        self.bus.publish("websocket-broadcast", "{}")

    def member_entered(self, member_object, gdpr_agreed):
        if gdpr_agreed == -1:
            messageType = BroadcastTypes.MEMBER_ENTERED_GDPR_CONSENT
        elif gdpr_agreed == 1:
            messageType = BroadcastTypes.MEMBER_ENTERED_CONSENT_GIVEN
        elif gdpr_agreed == 0:
            messageType = BroadcastTypes.MEMBER_ENTERED_CONSENT_DENIED

        self.bus.publish("websocket-broadcast",
                         json.dumps({
                             "messageType": messageType,
                             "messageData": {
                                 "userDetails": {
                                     "firstName": member_object.get("first_name"),
                                     "userId": member_object.get("user_id"),
                                     "gdprConsent": gdpr_agreed
                                 }
                             }}))
