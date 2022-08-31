import json
import pandas as pd
from xgboost import XGBClassifier


AWS_S3_BUCKET='churn-dataset'
def handler(event, context):
    
    # key = 'train.csv'
    # df = pd.read_csv(f"s3://{AWS_S3_BUCKET}/{key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello, World!')
    }
