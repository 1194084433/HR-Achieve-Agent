from fastapi import FastAPI

app = FastAPI(title="HR Archive Agent")

@app.get("/")
def root():
    return {"message": "HR Archive Agent is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
