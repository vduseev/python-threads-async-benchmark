from fastapi import FastAPI


app = FastAPI()


@app.get("/multiply")
async def multiply(number: int):
    result = number * 2
    return {
        "result": result
    }
