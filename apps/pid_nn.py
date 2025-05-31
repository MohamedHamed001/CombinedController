from flask import Blueprint, request, jsonify
import sys
import os

# Add the PID-NN-main directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../PID-NN-main'))

# Import the PID-NN app
from app import app as pid_nn_app

# Create blueprint
pid_nn_bp = Blueprint('pid_nn', __name__)

# Copy all routes from the original PID-NN app
for rule in pid_nn_app.url_map.iter_rules():
    if rule.endpoint != 'static':
        pid_nn_bp.add_url_rule(
            rule.rule,
            endpoint=rule.endpoint,
            view_func=pid_nn_app.view_functions[rule.endpoint],
            methods=rule.methods
        ) 