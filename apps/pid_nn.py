from flask import Blueprint, request, jsonify
import sys
import os

# Create blueprint
pid_nn_bp = Blueprint('pid_nn', __name__)

@pid_nn_bp.route('/status')
def status():
    return jsonify({"status": "PID-NN service is in maintenance mode"})

@pid_nn_bp.route('/health')
def health():
    return jsonify({"status": "healthy"})

@pid_nn_bp.route('/simulate', methods=['POST'])
def simulate():
    return jsonify({
        "status": "service temporarily unavailable",
        "message": "PID-NN simulation is currently in maintenance mode"
    })

@pid_nn_bp.route('/train', methods=['POST'])
def train():
    return jsonify({
        "status": "service temporarily unavailable",
        "message": "PID-NN training is currently in maintenance mode"
    })

# Add the PID-NN-main directory to the Python path
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../PID-NN-main'))
    # Import the PID-NN app
    from app import app as pid_nn_app

    # Copy all routes from the original PID-NN app
    for rule in pid_nn_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            pid_nn_bp.add_url_rule(
                rule.rule,
                endpoint=rule.endpoint,
                view_func=pid_nn_app.view_functions[rule.endpoint],
                methods=rule.methods
            )
except ImportError:
    # If TensorFlow is not available, the routes will not be registered
    pass 