web: gunicorn diabetes_companion.app:app --port $PORT
web2: gunicorn PID-NN-main.app:app --port $((PORT + 1)) 