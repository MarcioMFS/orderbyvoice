# Order by Voice

A Flask-based application for processing voice-based orders. This application allows users to place orders using voice commands, which are then processed and stored in a database.

## Features

- Voice-based order processing
- Text-to-speech conversion
- Order management
- Customer management
- RESTful API
- Web interface for testing

## Project Structure

```
orderbyvoice/
├── src/
│   ├── api/              # API endpoints and routes
│   ├── core/             # Core functionality
│   ├── models/           # Database models
│   ├── services/         # Business logic and services
│   ├── utils/            # Utility functions
│   └── config/           # Configuration files
├── interface_teste/      # Web interface files
├── temp/                 # Temporary files
├── tests/               # Test files
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/orderbyvoice.git
cd orderbyvoice
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
DATABASE_PATH=orderbyvoice.db
OPENAI_API_KEY=your-openai-api-key
SPEECH_MODEL=default
SPEECH_LANGUAGE=pt-BR
```

5. Initialize the database:
```bash
flask init-db
```

6. Run the application:
```bash
flask run
```

## API Documentation

The API documentation is available at `/docs` when the application is running.

### Endpoints

- `GET /`: Welcome message
- `GET /api/v1/pedidos`: List all orders
- `POST /api/v1/pedidos`: Create a new order
- `GET /api/v1/pedidos/<id>`: Get order details
- `GET /api/v1/clientes`: List all customers
- `POST /api/v1/clientes`: Create a new customer

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project uses Black for code formatting and Flake8 for linting:
```bash
black .
flake8
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 