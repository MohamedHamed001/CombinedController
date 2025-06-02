from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# Global variables to store latest glucose reading
latest_glucose = None
latest_glucose_time = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            global latest_glucose, latest_glucose_time
            latest_glucose = float(data['glucose'])
            latest_glucose_time = datetime.now()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'status': 'success',
                'message': 'Glucose reading updated successfully',
                'glucose': latest_glucose,
                'timestamp': latest_glucose_time.isoformat()
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