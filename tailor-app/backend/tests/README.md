# Backend Tests
This directory contains tests for the Flask backend application.

## Setup

Make sure you are in the backend directory
Install the required dependencies:
pip install -r requirements.txt


## Running Tests
To run the tests:
pytest
For more verbose output:
pytest -v
To generate a coverage report:
pytest --cov=.
To generate a detailed HTML coverage report:
pytest --cov=. --cov-report=html
Then open htmlcov/index.html in your browser to view the report.

## Test Structure
test_app.py - Tests for the main Flask application endpoints
conftest.py - Pytest configuration and fixtures

## nvironment Variables
The tests use mock environment variables. In production, make sure to set a .env file with:

COHERE_API_KEY = Your Cohere API key