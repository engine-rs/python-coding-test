#!/bin/bash

# Start the FastAPI server in the background
poetry run uvicorn src.main:app --reload &
SERVER_PID=$!

# Wait for a few seconds to ensure the server starts
sleep 10

# Kill the server process
kill $SERVER_PID