# -*- coding: utf-8 -*-
# + {}
import os; os.system('clear')
import numpy as np
from scipy import signal
import scipy
import pandas as pd

from ciervo.models import train_test_split
import ciervo.parameters as p
from ciervo.models import features_v1

# train model
from sklearn.ensemble import RandomForestClassifier

# svm
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

if __name__ == "__main__":
    # cargar data
    data = np.load('ciervo/models/recordings/parado1.npy')

    n_points = data.shape[1]
    print(f"Tiempo de grabación: {n_points/250} s")

    df = pd.DataFrame(data.T, columns=p.CH_NAMES)
    df['labels'] = df['MARKERS']
    # remove df['labels'] == 0
    df = df[df['labels'] != 0]
    df['labels'] = df['labels'].apply(lambda x: 1 if x == 2 else 0)

    train_data, train_label,  test_data, test_label = train_test_split([df], 
                                         columna=['C1', 'C2', 'C3', 'C4'],
                                         window_size=25,
                                         overlap=0, 
                                         test_size=0.2,
                                         random_state=42)
    print(train_data.shape, train_label.shape, test_data.shape, test_label.shape)

    # feature extraction
    train_features = []
    for i in range(len(train_data)):
        train_features.append(features_v1(train_data[i].T)[0])
    train_features = np.array(train_features)

    test_features = []
    for i in range(len(test_data)):
        test_features.append(features_v1(test_data[i].T)[0])
    test_features = np.array(test_features)

    print(train_features.shape, test_features.shape)
    print(train_label.shape, test_label.shape)

    clf = RandomForestClassifier()
    clf.fit(train_features, train_label)
    #y_pred = clf.predict(test_features)
    #print(accuracy_score(test_label, y_pred))
    #----------------------------------------------------------------------------------------------------
    
    # Usar predict_proba en lugar de predict, da probabilidad de c/clase [[prob clase 0, prob clase 1], [prob clase 0, prob clase 1]]
    y_proba = clf.predict_proba(test_features)

    # Ajustar umbral de clasificación
    custom_threshold = 0.5  # Puedes ajustar este valor
    y_pred_custom = (y_proba[:, 1] >= custom_threshold).astype(int)

    # Imprimir las probabilidades para cada muestra
    for i, prob in enumerate(y_proba):
        print(f"Muestra {i+1}: Probabilidad de 0: {prob[0]:.2f}, Probabilidad de 1: {prob[1]:.2f}")
    
    print("Accuracy con umbral personalizado:", accuracy_score(test_label, y_pred_custom))

    #----------------------------------------------------------------------------------------------------
    
    # save model
    import joblib
    joblib.dump(clf, 'model.pkl')

    # load model
    clf = joblib.load('model.pkl')
    #y_pred = clf.predict(test_features)
    #print(accuracy_score(test_label, y_pred))


