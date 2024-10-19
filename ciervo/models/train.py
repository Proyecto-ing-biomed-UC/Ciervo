import os; os.system('clear')
import numpy as np
from scipy import signal
import scipy
from ciervo.models import train_test_split
import pandas as pd
import ciervo.parameters as p
from ciervo.models import features_v1
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
import joblib



#otro6, otro5, viernes, last_day2, last_day
def remove_nan_values(features, labels):
    """Remove values with NaN values"""
    isnan = np.isnan(features).any(axis=1)

    features[isnan] = 0

    return features, labels

    


if __name__ == "__main__":
    # Load data
    files = ['otro6', 'otro5']

    data = []
    for file in files:
        temp = np.load(f'recordings/{file}.npy')
        print(temp.shape)
        data.append(temp)

    data = np.hstack(data)


    n_points = data.shape[1]
    print(f"Recording time: {n_points/250} s")

    df = pd.DataFrame(data.T, columns=p.CH_NAMES)
    df['labels'] = df['MARKERS']
    df = df[df['labels'] != 0]
    df['labels'] = df['labels'].apply(lambda x: 1 if x == 2 else 0)

    fig = plt.figure()

    plt.plot(df['labels'].to_numpy(), label='orig')

    # Smooth filter
    kernel_size = 200 
    df['labels'] = np.convolve(df['labels'].to_numpy(), np.array([1]*kernel_size) / kernel_size, mode='same')
    df['labels'] = np.convolve(df['labels'].to_numpy(), np.array([1]*kernel_size) / kernel_size, mode='same')
    df['labels'] = np.convolve(df['labels'].to_numpy(), np.array([1]*kernel_size) / kernel_size, mode='same')

    plt.plot(df['labels'].to_numpy(), label='filter')

    df['labels'] = df['labels'].apply(lambda x: 1 if x > 0.5 else 0)

    plt.plot(df['labels'].to_numpy(), label='final')
    plt.legend()

    plt.show()

    train_data, train_label, test_data, test_label = train_test_split([df], 
                                         columna=['C1', 'C2', 'C3', 'C4'],
                                         window_size=25,
                                         overlap=0, 
                                         test_size=0.1,
                                         random_state=42)
    
    print(train_data.shape, train_label.shape, test_data.shape, test_label.shape)

    # Feature extraction
    train_features = [features_v1(x.T)[0] for x in train_data]
    train_features = np.array(train_features)

    test_features = [features_v1(x.T)[0] for x in test_data]
    test_features = np.array(test_features)

    # Remove trials with NaN values
    train_features, train_label = remove_nan_values(train_features, train_label)
    test_features, test_label = remove_nan_values(test_features, test_label)


    print(train_features.shape, test_features.shape)
    print(train_label.shape, test_label.shape)

    # Classifier and parameter grid setup
    classifiers = {
        'RandomForest': RandomForestClassifier(),
        'SVC': make_pipeline(StandardScaler(), SVC())
    }

    param_grids = {
        'RandomForest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5],
        },
        'SVC': {
            'svc__C': [0.1, 1, 10],
            'svc__kernel': ['linear', 'rbf'],
        }
    }

    best_accuracy = 0.0
    best_clf = None
    best_name = ""

    for clf_name in classifiers:
        clf = classifiers[clf_name]
        param_grid = param_grids[clf_name]
        
        grid_search = GridSearchCV(clf, param_grid, cv=3, scoring='accuracy')
        grid_search.fit(train_features, train_label)

        print(f"{clf_name} best parameters: {grid_search.best_params_}")
        accuracy = accuracy_score(test_label, grid_search.predict(test_features))
        print(f"{clf_name} test accuracy: {accuracy * 100:.2f}%")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_clf = grid_search.best_estimator_
            best_name = clf_name

    print(f"Best classifier: {best_name} with accuracy: {best_accuracy * 100:.2f}%")
    
    # Save the best model
    joblib.dump(best_clf, 'model.pkl')

    # Load and test the saved best model
    loaded_clf = joblib.load('model.pkl')
    y_pred = loaded_clf.predict(test_features)
    print(f"Loaded model accuracy: {accuracy_score(test_label, y_pred) * 100:.2f}%")