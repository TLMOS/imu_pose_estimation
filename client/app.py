import uvicorn
from fastapi import File, UploadFile, FastAPI, Request, Form
import os
import yaml
import zipfile
app = FastAPI()

@app.post("/upload")
async def upload(request: Request, session_name: str = Form(...), file: UploadFile = File(...)):
    if request.headers.get('Type') == "session_part":
        try:
            with open('config.yml', 'r') as f:
                cfg = yaml.safe_load(f)
            sessions_path = cfg['path']['sessions_path']
            if not os.path.isdir(sessions_path):
                print('ERROR: Sessions dir does not exist!')
            dir = os.path.join(sessions_path, session_name)
            if not os.path.isdir(dir):
                os.mkdir(dir)
            contents = await file.read()
            file_path = os.path.join(dir, file.filename)
            with open(file_path, 'wb') as f:
                f.write(contents)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(dir)
            os.remove(file_path)
        except Exception as e:
            print("ERROR: ", e)
            return {"message": "There was an error uploading the file"}
        finally:
            await file.close()  
        return {"message": f"Successfuly uploaded {file.filename}"}
        
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)