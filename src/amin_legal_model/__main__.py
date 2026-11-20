import uvicorn


if __name__ == "__main__":
    uvicorn.run("amin_legal_model.api:app", host="127.0.0.1", port=8000, reload=False)
