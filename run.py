import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get environment or default to development
env = os.getenv('FLASK_ENV', 'development')

# Create app instance
app = create_app(env)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=env == 'development') 