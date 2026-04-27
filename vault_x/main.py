import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from security import encrypt_file_data, decrypt_file_data

app = FastAPI()

# Enable CORS so your frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "VAULT-X2 ONLINE", "mode": "BINARY_STREAMING_ACTIVE"}

@app.post("/process-file")
async def process_file(
    action: str = Form(...), 
    password: str = Form(...), 
    file: UploadFile = File(...)
):
    try:
        # Read the binary file into memory
        file_bytes = await file.read()
        
        if action == "encrypt":
            result_bytes = encrypt_file_data(file_bytes, password)
            # Append .vx2 to the original filename
            output_filename = f"{file.filename}.vx2"
        elif action == "decrypt":
            result_bytes = decrypt_file_data(file_bytes, password)
            # Remove .vx2 to restore original extension
            output_filename = file.filename.replace(".vx2", "")
        else:
            raise HTTPException(status_code=400, detail="Invalid Action")

        # Stream the file back to the browser for automatic download
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
        
    except Exception as e:
        # Usually triggered by wrong password or corrupted file
        raise HTTPException(
            status_code=400, 
            detail="Authentication Failed: Incorrect Master Key or Corrupted Data."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)