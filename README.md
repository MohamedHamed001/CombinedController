# Combined Controller Project

This project contains two separate applications:
1. Diabetes Companion - A chatbot application for diabetes management
2. PID-NN - A neural network-based PID controller

## Project Structure
```
.
├── diabetes_companion/     # Diabetes Companion application
├── PID-NN-main/           # PID-NN application
├── requirements.txt       # Combined dependencies
├── Procfile              # Deployment configuration
└── README.md             # This file
```

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

### Diabetes Companion
```bash
cd diabetes_companion
python app.py
```

### PID-NN
```bash
cd PID-NN-main
python app.py
```

## Deployment

The project is configured for deployment with the following considerations:

1. Both applications run on separate ports
2. Environment variables needed:
   - `PORT`: Port for Diabetes Companion app
   - `PORT2`: Port for PID-NN app
   - Other environment-specific variables (check respective app configurations)

### Deployment Steps

1. Ensure all environment variables are set in your deployment platform
2. The Procfile is configured to run both applications
3. Dependencies are managed through the root requirements.txt

## API Routes

### Diabetes Companion
- Base URL: `http://localhost:5000` (default)
- API endpoints are defined in `diabetes_companion/app.py`

### PID-NN
- Base URL: `http://localhost:5001` (default)
- API endpoints are defined in `PID-NN-main/app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

