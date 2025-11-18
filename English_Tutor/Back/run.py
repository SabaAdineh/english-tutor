import uvicorn

if __name__ == "__main__":
    print("🚀 Starting English Tutor Backend...")
    print("📡 Local URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs") 
    print("💡 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)