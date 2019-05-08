import os
import cherrypy
import json
import random
import xmltodict
import re
import string
from lib.net2.wrapper import Net2Wrapper
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from lib.webserver.websocket import OpenBotWebSocketHandler, OpenBotWebSocketPlugin


class PaxtonRequestHandler():
    def __init__(self, app):
        self.app = app
        cherrypy.tree.mount(self,
                            "/webservice/service.asmx", {"/": {"tools.trailing_slash.on": False,
                                                               "tools.trailing_slash.missing": True}})

    @cherrypy.expose
    def index(self):
        try:
            cl = cherrypy.request.headers['Content-Length']
            rawbody = cherrypy.request.body.read(int(cl))
            parser = re.compile(b"<body>(.+?)</body>")
            (request_body,) = parser.findall(rawbody)
            self.handle_request(request_body.decode("utf-8").split(","))
        except Exception as e:
            print(e)

    @cherrypy.tools.json_out()
    def does_user_have_access(self, username):
        user_record = self.app.net2.user_has_access(username)
        return user_record

    def handle_request(self, parsed_body):
        (date, time, event_id, username, door_name,
         description, address, card_number) = parsed_body

        (user_has_access, user_record) = self.does_user_have_access(username)
        if not user_has_access:
            return {"status": "Access Denied"}
        else:
            gdpr_accepted = self.app.member_db.user_accepted_gdpr(user_record)
            cherrypy.engine.websockets.member_entered(
                user_record, gdpr_accepted)


class Webserver():
    def __init__(self, application):
        self.app = application
        self.PaxtonRequestHandler = PaxtonRequestHandler(application)

        if ("API_KEY" not in os.environ):

            print(
                "[HTTP] API key not supplied in environment variables. Using 'dev' key.")
            self.api_key = "devkey".encode("UTF-8")
        else:
            self.api_key = os.environ["API_KEY"].encode("UTF-8")
        cherrypy.config.update("config/webserver.conf")
        cherrypy.engine.websockets = OpenBotWebSocketPlugin(cherrypy.engine)
        cherrypy.tools.websocket = WebSocketTool()

        cherrypy.engine.net2 = self.app.net2
        cherrypy.engine.serverVersion = "1.0.0"

        cherrypy.tree.mount(self, config={'/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': OpenBotWebSocketHandler}})

        cherrypy.tools.cors = cherrypy._cptools.HandlerTool(self.cors)

    @cherrypy.expose
    def open_door(self):
        try:
            self.app.net2.open_door()
        except Exception as e:
            print(e)

    def callback(self):
        print("[HTTP] Started Webserver ({0}:{1})".format(cherrypy.config.get(
            "server.socket_host"), cherrypy.config.get("server.socket_port")))

    def start(self):
        OpenBotWebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()
        cherrypy.engine.start_with_callback(self.callback)

    def stop(self):
        cherrypy.engine.exit()

    def cors(self):
        if cherrypy.request.method == 'OPTIONS':
            # preflight request
            # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
            # tell CherryPy no avoid normal handler
            return True
        else:
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

    @cherrypy.expose
    def index(self):
        return "Hello World"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def register(self, api_key=None):
        if api_key.encode("UTF-8") == self.api_key:
            result = self.app.websocket_db.generate_websocket_token()
            (success, token) = result
            if success:
                return {"status": "Success", "success": True, "action": "/register", "token": token}
            else:
                return {"status": "Error", "success": False, "action": "/register"}
        else:
            return {"status": "Access Denied", "success": False, "action": "/register"}

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST', 'OPTIONS'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def gdpr_response(self, *args, ** kwargs):
        data = cherrypy.request.json
        user_id = data.get("userId")
        response = data.get("response")
        self.app.member_db.update_gdpr(user_id, response)
        return {"status": "success"}

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler.set_variable(
            "serverVersion", "1")
        cherrypy.request.ws_handler
