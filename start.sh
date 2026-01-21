#!/bin/bash

echo "🏥 Starting The Equalizer..."
echo ""

# Check if .env exists in backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found in backend/"
    echo "   Creating from template..."
    cp backend/.env.example backend/.env
    echo "   Please add your ANTHROPIC_API_KEY to backend/.env"
    echo ""
fi

# Start backend
echo "🔧 Starting backend server on http://localhost:8000..."
cd backend
/Users/pratikjaluka/Library/Python/3.12/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ The Equalizer is running!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
