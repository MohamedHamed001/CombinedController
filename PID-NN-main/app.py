from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from .src.artificial_pancreas_simulator import InsulinSimulator
import os
import requests
import json
from datetime import datetime
import time
import math

app = Flask(__name__)
# Enable CORS for all routes and allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
DEFAULT_WEIGHT = 70.0

# Initialize the insulin simulator with default values
simulator = None
latest_glucose = None
latest_glucose_time = None
patient_weight = float(os.getenv('PATIENT_WEIGHT', DEFAULT_WEIGHT))

def initialize_simulator(weight=DEFAULT_WEIGHT):
    """Initialize the insulin simulator with the trained model."""
    global simulator
    model_path = os.path.join('models', 'nn_pid_tuning_model.h5')
    print(f"Loading model from: {model_path}")
    print(f"Model exists: {os.path.exists(model_path)}")
    
    print("Initializing simulator with:")
    print(f"- Model path: {model_path}")
    print(f"- Weight: {weight} kg")
    print(f"- Simulation time: 24 hours")
    
    simulator = InsulinSimulator(model_path, None, 24 * 60 * 60 * 10**9)  # 24 hours in nanoseconds
    print("Simulator initialized successfully")

@app.route('/update_glucose', methods=['POST'])
def update_glucose():
    """Update the latest glucose reading from the Flutter app."""
    try:
        print("\n=== Received update_glucose request ===")
        print(f"Request data: {request.get_data()}")
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        if 'glucose' not in data:
            print("Error: No glucose value in request")
            return jsonify({
                'status': 'error',
                'message': 'Glucose value is required'
            }), 400
        
        global latest_glucose, latest_glucose_time
        latest_glucose = float(data['glucose'])
        latest_glucose_time = datetime.now()
        
        print(f"Updated glucose reading: {latest_glucose} mg/dL at {latest_glucose_time}")
        print("=== End of update_glucose request ===\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Glucose reading updated successfully',
            'glucose': latest_glucose,
            'timestamp': latest_glucose_time.isoformat()
        })
    except Exception as e:
        print(f"Error in update_glucose: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/update_patient', methods=['POST'])
def update_patient():
    """Update patient data."""
    try:
        data = request.get_json()
        if 'weight' in data:
            global patient_weight
            patient_weight = float(data['weight'])
            
            # Reinitialize simulator with new weight
            global simulator
            simulator = None
            initialize_simulator(patient_weight)
            
            return jsonify({
                'status': 'success',
                'message': 'Patient data updated successfully'
            })
        return jsonify({
            'status': 'error',
            'message': 'Weight is required'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/predict', methods=['GET'])
def predict():
    """Predict insulin rate based on current glucose reading."""
    print("\n=== Predict endpoint called ===")
    
    # Get the latest glucose reading from global variables
    global latest_glucose, latest_glucose_time, patient_weight
    print(f"Latest glucose: {latest_glucose}")
    print(f"Latest glucose time: {latest_glucose_time}")
    
    if not latest_glucose:
        print("No glucose reading available")
        return jsonify({"error": "No glucose reading available"}), 400
    
    # Get patient weight from the request or use stored value
    weight = request.args.get('weight', type=float)
    if not weight:
        weight = patient_weight
    print(f"Using patient weight: {weight} kg")
    
    # Get current time in nanoseconds
    current_time_ns = int(time.time_ns())
    print(f"Current glucose reading: {latest_glucose} mg/dL")
    print(f"Current time (ns): {current_time_ns}")
    
    try:
        # Initialize simulator with current time
        simulator = InsulinSimulator(
            model_path='models/nn_pid_tuning_model.h5',
            test_case_path=None,
            totalSimulationTimeInNs=current_time_ns
        )
        
        print("Running simulator...")
        # Get insulin rate from simulator
        insulin_rate = simulator.run(latest_glucose, current_time_ns)
        print(f"Raw insulin rate from simulator: {insulin_rate}")
        print(f"Type of insulin_rate: {type(insulin_rate)}")
        
        # If simulator returns None, calculate a default basal rate
        if insulin_rate is None:
            print("Simulator returned None, calculating default basal rate")
            # Calculate default basal rate based on weight (0.5 U/kg/day)
            default_basal = (0.5 * weight) / 24  # Convert daily rate to hourly
            insulin_rate = max(0.1, default_basal)  # Ensure minimum rate of 0.1 U/hr
            print(f"Using default basal rate: {insulin_rate} U/hr")
        
        # Ensure we have a valid number
        if not isinstance(insulin_rate, (int, float)) or math.isnan(insulin_rate):
            print("Warning: Invalid insulin rate:", insulin_rate)
            # Calculate default basal rate based on weight
            default_basal = (0.5 * weight) / 24
            insulin_rate = max(0.1, default_basal)
            print(f"Using default basal rate: {insulin_rate} U/hr")
        
        # Ensure minimum rate of 0.1 U/hr
        insulin_rate = max(0.1, insulin_rate)
        
        print(f"Final insulin rate: {insulin_rate} U/hr")
        print("=== End of predict request ===\n")
        
        return jsonify({
            "insulin_rate": insulin_rate,
            "units_per_hour": insulin_rate
        })
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port) 