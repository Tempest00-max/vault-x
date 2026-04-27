import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from security import encrypt_file, decrypt_file
import io

app = FastAPI()

# --- THE HANDSHAKE (CORS) ---
# This allows your GitHub site to talk to your Railway server
origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "https://tempest00-max.github.io", # Your live frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Vault-X2 Engine Active", "mode": "Obsidian"}

# --- THE BINARY ENGINE ---

@app.post("/process-file")
async def process_file(
    file: UploadFile = File(...), 
    password: str = Form(...), 
    mode: str = Form(...)
):
    try:
        # Read the file into memory (Streaming small to medium files)
        file_data = await file.read()
        
        if mode == "encrypt":
            processed_data = encrypt_file(file_data, password)
            filename = f"{file.filename}.vx2"
        elif mode == "decrypt":
            processed_data = decrypt_file(file_data, password)
            # Remove .vx2 extension if it exists
            filename = file.filename.replace(".vx2", "")
        else:
            raise HTTPException(status_code=400, detail="Invalid Mode")

        # Stream the file back to the user's browser
        return StreamingResponse(
            io.BytesIO(processed_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        # If decryption fails (wrong password), send a 401
        raise HTTPException(status_code=401, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)