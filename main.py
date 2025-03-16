import os
import uvicorn
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()

# Health check route (useful for debugging)
@app.get("/")
def home():
    return {"message": "🚀 Paraclete AI is live on Render!"}

# Get the port from environment (Render provides this dynamically)
PORT = int(os.getenv("PORT", 8000))  # Default to 8000 if not set

# Debugging: Print the port on startup
print(f"🔧 Starting Uvicorn on port {PORT}...")

# Run Uvicorn server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)





