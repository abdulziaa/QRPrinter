from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from os import listdir
from os.path import join, isfile
import asyncio
from typing import List
import ssl


app = FastAPI()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./cert.pem', keyfile='./key.pem')

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (you might want to restrict this in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

def clear_files_directory():
    directory = "./files"
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

async def clear_files_periodically():
    while True:
        await asyncio.sleep(300)  # Wait for 5 minutes
        clear_files_directory()

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_path = os.path.join("./files", file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(file.filename)
    return {"saved_files": saved_files}


@app.get("/files")
async def get_files():
    files = [f for f in listdir("./files") if isfile(join("./files", f))]
    return {"files": files}

@app.get("/file/{filename}")
async def get_file(filename: str):
    file_path = join("./files", filename)
    if isfile(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

@app.on_event("startup")
async def startup_event():
    # Start the background task to clear files periodically
    asyncio.create_task(clear_files_periodically())
    
    # Clear files directory when application starts
    clear_files_directory()