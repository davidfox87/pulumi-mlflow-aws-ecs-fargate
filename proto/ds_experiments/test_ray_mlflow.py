#!/usr/bin/env python
"""Examples using MLfowLoggerCallback and mlflow_mixin.
"""
import os
import tempfile
import time

import mlflow

from ray import tune
from ray.tune.tuner import Tuner
from ray.tune.search.hyperopt import HyperOptSearch
from ray.tune.integration.mlflow import mlflow_mixin

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt


X, y = load_iris(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.9, shuffle=False)

@mlflow_mixin
def train_fn(config):
    # Hyperparameters
    max_depth, n_estimators, max_features = config["max_depth"], config["n_estimators"], config["max_features"]
    hparams = {
            "n-estimators": n_estimators,
            "max_depth": max_depth,
            "max_features": max_features
    }
    mlflow.log_params(hparams)

    model = RandomForestClassifier(n_estimators=n_estimators,
                                    max_depth=max_depth,
                                    n_jobs=-1
            )

    model.fit(X_train, y_train)

    score = cross_val_score(model, X_train, y_train, cv=5).mean()

    # Log the metrics to mlflow
    mlflow.log_metrics(dict(accuracy=score))

    # Feed the score back to Tune.
    tune.report(loss=score, done=True)


def tune_decorated(mlflow_tracking_uri, mlflow_experiment_name):
    # Set the experiment, or create a new one if does not exist yet.
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name=mlflow_experiment_name)
    algo = HyperOptSearch()

    tuner = Tuner(trainable=train_fn, 
                tune_config=tune.TuneConfig(search_alg=algo, num_samples=5, metric="loss", mode="max"),
                param_space={'max_features': tune.choice([1, 2]),
                            'max_depth': tune.qrandint(2, 4, 1),
                            'n_estimators': tune.qrandint(200, 400, 100),
                            "mlflow": {"experiment_name": mlflow_experiment_name,
                                        "tracking_uri": mlflow.get_tracking_uri()
                            }
                }
                    
    )

    tuner.fit()



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--tracking-uri",
        type=str,
        help="The tracking URI for the MLflow "
        "tracking server.")
    
    parser.add_argument(
        "--experiment-name",
        type=str,
        help="The name of the MLflow experiment.")
    
    parser.add_argument(
        "--server-address",
        type=str,
        default=None,
        required=False,
        help="The address of server to connect to if using "
        "Ray Client.")

    args, _ = parser.parse_known_args()

    if args.server_address:
        import ray
        ray.init(f"ray://{args.server_address}")

    if args.server_address and not args.tracking_uri:
        raise RuntimeError("If running this example with Ray Client, "
                           "the tracking URI for your tracking server should"
                           "be explicitly passed in.")

   
    mlflow_tracking_uri = args.tracking_uri
    mlflow_experiment_name = args.experiment_name

    tune_decorated(mlflow_tracking_uri, mlflow_experiment_name)
    
    df = mlflow.search_runs(
        [mlflow.get_experiment_by_name(mlflow_experiment_name).experiment_id])
    run_id = df.loc[df['metrics.accuracy'].idxmax(), :]['run_id']
    print(run_id)
    mlflow.set_tag("best params", run_id)
    # build a model and save artifact using these parameters

    # mlflow.sklearn.log_model(
    #         sk_model=model,
    #         artifact_path="sklearn-model",
    #         registered_model_name="sk-learn-random-forest-clf-model"
    #     )