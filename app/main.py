from fastapi import FastAPI, Request
import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json


app = FastAPI()

templates = Jinja2Templates(directory="test/templates")
app.mount("/node_modules", StaticFiles(directory="test/node_modules"), name="node_modules")

data = pd.read_csv("data/uchazeci_transformed.csv")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/okruhy")
def get_okruhy(request: Request):
    okruhy_df = data[["OKRUH1", "OKRUH2"]].dropna()
    pivot_table = okruhy_df.pivot_table(
        index="OKRUH1", columns="OKRUH2", aggfunc=len, fill_value=0
    )
    okruh1_counts = okruhy_df["OKRUH1"].value_counts()
    okruh2_counts = okruhy_df["OKRUH2"].value_counts()
    
    json_data = {
        "pivot_table": pivot_table.to_json(),
        "okruh1_counts": okruh1_counts.to_json(),
        "okruh2_counts": okruh2_counts.to_json(),
    }
    
    return json_data