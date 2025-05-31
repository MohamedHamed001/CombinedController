from flask import Blueprint, request, jsonify
import sys
import os

# Add the diabetes_companion directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../diabetes_companion'))

# Import the diabetes companion app
from app import app as diabetes_companion_app

# Create blueprint
diabetes_companion_bp = Blueprint('diabetes_companion', __name__)

# Copy all routes from the original diabetes companion app
for rule in diabetes_companion_app.url_map.iter_rules():
    if rule.endpoint != 'static':
        diabetes_companion_bp.add_url_rule(
            rule.rule,
            endpoint=rule.endpoint,
            view_func=diabetes_companion_app.view_functions[rule.endpoint],
            methods=rule.methods
        ) 