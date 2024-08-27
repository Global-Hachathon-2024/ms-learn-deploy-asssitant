# main.py
from fastapi import FastAPI

app = FastAPI()

# just for health check
@app.get("/ping")
async def ping():
    return "pong"

# generate ARM template
@app.post("/templates")
async def generate_arm_template(url: str):

    # TODO: validate an input URL

    # TODO: retrieve its web page content

    # TODO: make a prompt texts 

    # TODO: request AOAI to generate a ARM template

    # TODO: validate if a generated ARM template is valid

    # TODO: if valid, save it to our GitHub repository

    # TODO: if invalid, get an error message and retry to generate a ARM template with some information

    # TODO: store the generate result to our database

    return f"ARM template for {url} generated successfully"