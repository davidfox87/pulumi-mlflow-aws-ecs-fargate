import pandas as pd
from sklearn.model_selection import train_test_split


def preprocess_raw_data():
    """
    Reads raw data from local and makes pre-processing necessary to use dataset with XGBoost.
    """

    churn = pd.read_csv('..data/churn.csv')
    churn = churn.drop('Phone', axis=1)
    churn['Area Code'] = churn['Area Code'].astype(object)

    churn = churn.drop(['Day Charge', 'Eve Charge', 'Night Charge', 'Intl Charge'], axis=1)

    model_data = pd.get_dummies(churn)
    model_data = pd.concat([model_data['Churn?_True.'], model_data.drop(['Churn?_False.', 'Churn?_True.'], axis=1)], axis=1)

    train_data, test_data = train_test_split(model_data, train_size=0.9)
    train_data, validation_data = train_test_split(train_data, train_size=0.75)

    train_data.to_csv('../data/train.csv', header=False, index=False)
    validation_data.to_csv('../data/validation.csv', header=False, index=False)

def fit_model():
    print("hello from fit_model")

def predict():
    print("hello from predict")