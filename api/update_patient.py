from http.server import BaseHTTPRequestHandler
import json
import os

# Default weight
DEFAULT_WEIGHT = 70.0
patient_weight = float(os.getenv('PATIENT_WEIGHT', DEFAULT_WEIGHT))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            if 'weight' in data:
                global patient_weight
                patient_weight = float(data['weight'])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'message': 'Patient data updated successfully'
                }).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': 'Weight is required'
                }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': str(e)
            }).encode()) 