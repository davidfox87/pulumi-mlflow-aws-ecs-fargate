# MLOps platform prototype
This app uses MLFlow to take the best performing model and use that to serve predictions in 
production

The ML model is served using FASTAPI

To test the predict endpoint, send some data via CURL

curl -X POST http://localhost:3000/predict -H 'Content-Type: application/json' -d '{"sepal": {"length": 5.0, "width": 3.0}, "petal": {"length": 4.0, "width": 2.0}}'