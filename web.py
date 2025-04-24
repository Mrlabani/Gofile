from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "GoFile Uploader Bot is running!"}
