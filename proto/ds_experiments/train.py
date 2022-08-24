import os
import logging
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.INFO)


if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    # MLflow related parameters
    parser.add_argument("--tracking_uri", type=str, default="http://alb-7f4ea18-958960412.us-west-1.elb.amazonaws.com")
    parser.add_argument("--experiment_name", type=str)

    args, _ = parser.parse_known_args()


    logging.info('reading data')
    # prepare example dataset
    X, y = load_iris(return_X_y=True, as_frame=True)


    logging.info('building training and testing datasets')
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    

    # set remote mlflow server
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment_name)
    
    with mlflow.start_run():
        params = {
            "n-estimators": 10,
            "min-samples-leaf": 3,
            "features": list(X_train.columns)
        }
        mlflow.log_params(params)
        
        # TRAIN
        logging.info('training model')
        model = RandomForestClassifier(
            n_estimators=10,
            min_samples_leaf=3,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # log F1 score
        logging.info('evaluating model')
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        logging.info('accuracy %s', acc)
        mlflow.log_metric('accuracy', acc)

        # SAVE MODEL
        logging.info('saving model in MLflow')
        mlflow.sklearn.log_model(model, "model")


