from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from apps.pid_nn import pid_nn_bp
from apps.diabetes_companion import diabetes_companion_bp

app = Flask(__name__)
CORS(app)

# Register blueprints with URL prefixes
app.register_blueprint(pid_nn_bp, url_prefix='/pid-nn')
app.register_blueprint(diabetes_companion_bp, url_prefix='/diabetes-companion')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "services": ["pid-nn", "diabetes-companion"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 