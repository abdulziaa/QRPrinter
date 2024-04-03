from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.responses import FileResponse
from os import listdir
from os.path import isfile, join
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (you might want to restrict this in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile] = File(...)):
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
