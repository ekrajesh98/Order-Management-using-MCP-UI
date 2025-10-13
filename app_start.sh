#!/bin/bash
set -e

echo "Starting order management chatbot front end app..."

# use APP_PORT environment variable
streamlit run src/main.py --server.port $APP_PORT