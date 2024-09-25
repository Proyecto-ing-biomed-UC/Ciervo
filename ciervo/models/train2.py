# -*- coding: utf-8 -*-
import os; os.system('clear')
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
import joblib

from ciervo.models import train_test_split  # Importar tu función de división de datos
import ciervo.parameters as p
from ciervo.models import features_v1

# Cargar datos
data = np.load('ciervo/models/recordings/parado1.npy')

n_points = data.shape[1]
print(f"Tiempo de grabación: {n_points / 250} s")

df = pd.DataFrame(data.T, columns=p.CH_NAMES)
df['labels'] = df['MARKERS']
df = df[df['labels'] != 0]
df['labels'] = df['labels'].apply(lambda x: 1 if x == 2 else 0)

# Dividir los datos usando tu función
train_data, train_label, test_data, test_label = train_test_split(
    [df],
    columna=['C1', 'C2', 'C3', 'C4'],
    window_size=25,
    test_size=0.2,
    overlap=0,
    random_state=42
)

print(train_data.shape, train_label.shape, test_data.shape, test_label.shape)

# Extracción de características
train_features = [features_v1(data.T)[0] for data in train_data]
train_features = np.array(train_features)

test_features = [features_v1(data.T)[0] for data in test_data]
test_features = np.array(test_features)

print(train_features.shape, test_features.shape)
print(train_label.shape, test_label.shape)

# Ajuste de hiperparámetros con GridSearchCV
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

# Configurar GridSearchCV
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(train_features, train_label)

# Mejor modelo
best_clf = grid_search.best_estimator_
print(f"Mejores parámetros: {grid_search.best_params_}")

# Predicciones con el mejor modelo
y_pred = best_clf.predict(test_features)
accuracy = accuracy_score(test_label, y_pred)
print(f"Accuracy del mejor modelo: {accuracy:.2f}")

# Obtener probabilidades
y_proba = best_clf.predict_proba(test_features)

# Ajustar umbral de clasificación
custom_threshold = 0.5  # Puedes ajustar este valor
y_pred_custom = (y_proba[:, 1] >= custom_threshold).astype(int)

# Imprimir resultados
for i, prob in enumerate(y_proba):
    print(f"Muestra {i+1}: Probabilidad de 0: {prob[0]:.2f}, Probabilidad de 1: {prob[1]:.2f}")

print("Accuracy con umbral personalizado:", accuracy_score(test_label, y_pred_custom))

# Guardar el modelo
joblib.dump(best_clf, 'model.pkl')

# Cargar el modelo
clf = joblib.load('model.pkl')
y_pred = clf.predict(test_features)
print(accuracy_score(test_label, y_pred))
