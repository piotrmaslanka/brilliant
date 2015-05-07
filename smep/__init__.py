"""SMEP, or Some Moar Enterpricey Python.
A single web servering component for JSON"""
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi, json

class SMEPHandler(BaseHTTPRequestHandler):
    """Base class for web event handlers"""
    
    def post(self, arguments):
        """Override this. This should call .respond() at some point"""
        self.respond('Not implemented. Override me!', 500)            
        
    def respond(self, data, statusCode=200, contentType='application/json'):
        """Writes back data.
        If data is a string, it will be output as is. If it is an object, it will be JSON-ized."""
        
        if not isinstance(data, str):
            data = json.dumps(data)
        
        if statusCode == 200:
            self.send_response(statusCode)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(statusCode)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        postvars = dict(((k, v[0]) for k, v in postvars.iteritems()))        
        
        self.post(postvars)    

class _SMEPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True    
    
def start_smep(ifc, handlerInstance):
    """Start a SMEP server. Will be started as a daemon"""
    sms = _SMEPServer(ifc, handlerInstance)
    t = Thread(target=sms.serve_forever)
    t.daemon = True
    t.start()