import BaseHTTPServer # type: ignore
import json
from robot import Robot

global robot

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/act":
            content_length = int(self.headers.getheader('Content-Length'))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                client = str(data.get("client"))
                state = str(data.get("state"))
                action = str(data.get("action"))
                additional_data = str(data.get("additional_data", {}))

                # Log received data
                print("Received data from client:")
                print("  Client: "+client)
                print("  State: "+state)
                print("  Action: "+ action)
                print("  Additional Data: " + additional_data)
                print(action == 'say')
                
                if action == 'say':
                    robot.say(additional_data)
                elif action == 'move':
                    if additional_data == 'bigcircle':
                        robot.bigcircle(action[2])
                    elif additional_data == 'push':
                        robot.pushout(action[2])

                # Respond with a success message
                response = {
                    "status": "success",
                    "message": "Data received",
                    "client": client,
                    "state": state,
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response))
            except Exception as e:
                # Handle JSON parsing or other errors
                self.send_response(400)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write("Error processing request: "+ str(e))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Endpoint not found")
        


def RobotCommunicator(server_class=BaseHTTPServer.HTTPServer, handler_class=RequestHandler, port=9001):
    global robot
    robot = Robot(44821)
    server_address = ('172.17.0.1', port)
    httpd = server_class(server_address, handler_class)
    print("Python 2 HTTP server running on port "+str(port))
    httpd.serve_forever()
