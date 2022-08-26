import os
import uvicorn
import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging 

class FlowerPartSize(BaseModel):
    length: float
    width: float

class PredictRequest(BaseModel):
    sepal: FlowerPartSize
    petal: FlowerPartSize


app = FastAPI()
try:
    mlflow.set_tracking_uri(os.environ.get('TRACKING_URI')) # register the mlflow-server ecs address with cloudmap
except Exception as e:
   logging.error('Error at %s', 'TRACKING_URI', exc_info=e)

# Load model
model_name = 'sk-learn-random-forest-clf-model'
model = mlflow.pyfunc.load_model(
        model_uri=f"models:/{model_name}/Production"
)

flower_name_by_index = {0: 'Setosa', 1: 'Versicolor', 2: 'Virginica'}

@app.post("/predict")
def predict(request: PredictRequest):
    df = pd.DataFrame(columns=['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
                      data=[[request.sepal.length, request.sepal.width, request.petal.length, request.petal.width]])

    y_pred = model.predict(df)[0]
    return {"flower": flower_name_by_index[y_pred]}
