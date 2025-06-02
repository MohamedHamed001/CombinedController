from http.server import BaseHTTPRequestHandler
from src.artificial_pancreas_simulator import InsulinSimulator
import json
import os
import time

# Initialize simulator
simulator = InsulinSimulator(
    model_path='models/nn_pid_tuning_model.h5',
    test_case_path=None,
    totalSimulationTimeInNs=int(time.time_ns())
)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get latest glucose from query parameters
            glucose = float(self.path.split('glucose=')[1].split('&')[0])
            weight = float(self.path.split('weight=')[1]) if 'weight=' in self.path else 70.0
            
            # Get insulin rate from simulator
            insulin_rate = simulator.run(glucose, int(time.time_ns()))
            
            # If simulator returns None, calculate default basal rate
            if insulin_rate is None:
                default_basal = (0.5 * weight) / 24
                insulin_rate = max(0.1, default_basal)
            
            # Ensure minimum rate
            insulin_rate = max(0.1, insulin_rate)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                "insulin_rate": insulin_rate,
                "units_per_hour": insulin_rate
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                "error": str(e)
            }).encode()) 