#pip install ciervo --upgrade
#git clone https://github.com/domingomery/balu3
#pip install ./balu3

#balu3
from balu3.fs.sel  import sfs, clean        
from balu3.ft.norm import minmax 

#ciervo
#from ciervo.io import example_marcha, example_marcha_larga

#signals
from scipy import signal
import scipy.signal
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
import numpy as np   

#selector/transformer
from sklearn.cross_decomposition import PLSRegression
from balu3.ft.trans import pca                                                 
from sklearn.decomposition import FastICA  

# classifiers
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.neighbors import NearestCentroid                           
from sklearn.naive_bayes import GaussianNB                              
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis 
from sklearn.tree import DecisionTreeClassifier                         
from sklearn.ensemble import RandomForestClassifier                     
from sklearn.linear_model import LogisticRegression      
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis    
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.neighbors import KernelDensity
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier, BaggingClassifier
from sklearn.linear_model import Perceptron, SGDClassifier 

# cross validation
from sklearn.model_selection import cross_val_score

# Evaluation
from sklearn.metrics   import confusion_matrix, accuracy_score    

#Redes Neuronales
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import confusion_matrix, accuracy_score    
import torch.nn.functional as F

#Funcion extraccion caracteristicas
def extract_feature(data, divide=3):
    # data : (T, 4) 
    # T numero de muestras, 4 canales de EMG
    # C numero de indices de canales a usar
    # divide: divide la señal en partes iguales
    _, C = data.shape
    result = []
    feature_names = []

    for c in range(C):
        signal0 = data[:, c]

        # Full wave rectification
        rectified_signal = np.abs(signal0)

        #envolvente
        env = np.abs(signal.hilbert(data[:, c]))

        #RMS
        rms = np.sqrt(np.mean(rectified_signal**2))
        result.append(rms)
        feature_names.append(f"rms_channel_{c}")

        #Varianza
        var = np.var(rectified_signal)
        result.append(var)
        feature_names.append(f"var_channel_{c}")

        #kurtosis
        kurt = scipy.stats.kurtosis(rectified_signal)
        result.append(kurt)
        feature_names.append(f"kurt_channel_{c}")

        #skewness
        skew = scipy.stats.skew(rectified_signal)
        result.append(skew)
        feature_names.append(f"skew_channel_{c}")

        #zero crossing
        zc = ((signal0[:-1] * signal0[1:]) < 0).sum()
        result.append(zc)
        feature_names.append(f"zc_channel_{c}")

        #Frecuencias
        freqs, power_spectrum = scipy.signal.welch(signal0, fs=250, nperseg=32)
        median_freq = freqs[np.where(np.cumsum(power_spectrum) >= np.sum(power_spectrum) / 2)[0][0]]
        mean_freq = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)
        peak_freq = freqs[np.argmax(power_spectrum)]

        result.extend([median_freq, mean_freq, peak_freq])
        feature_names.extend([f"median_freq_channel_{c}", f"mean_freq_channel_{c}", f"peak_freq_channel_{c}"])


        #SEGMENTOS
        for i in range(divide):
            start = int(i*len(data)/divide)
            end = int((i+1)*len(data)/divide)

            segment_env = env[start:end]
            mean_env = segment_env.mean()
            std_env = segment_env.std()
            max_env = segment_env.max()
            min_env = segment_env.min()

            result.extend([mean_env, std_env, max_env, min_env])
            feature_names.extend([f"mean_env_segment_{i}channel{c}", f"std_env_segment_{i}channel{c}",
                                  f"max_env_segment_{i}channel{c}", f"min_env_segment_{i}channel{c}"])

    result = np.array(result)
    return result, feature_names

def label_data_and_features(data, divide=3):
    features =[]
    for d in tqdm(data):
      f,_ = extract_feature(d, divide)
      features.append(f)
    features = np.array(features) # (1000, features)
    return features

def clean_normalized_feature_selection(train_data, test_data):
    sclean = clean(train_data)  # Indices of selected features
    train_data, test_data = train_data[:, sclean], test_data[:, sclean]
    train_data, a, b = minmax(train_data)
    test_data = test_data * a + b
    return train_data, test_data


def sfs_selection(train_data, test_data,train_labels, n_indices):
    train_data, test_data = clean_normalized_feature_selection(train_data, test_data)
    sfs_indices = sfs(train_data, train_labels, n_indices) 
    train_data = train_data[:,sfs_indices] 
    test_data  =  test_data[:,sfs_indices] 
    print(sfs_indices)
    return train_data, test_data #,sfs_indices10,20,

def pca_tranformer(train_data, test_data,n_components):
  train_data, test_data = clean_normalized_feature_selection(train_data, test_data)
  train_data, _, A, Xm, _ = pca(train_data, n_components=n_components)
  test_data = np.matmul(test_data- Xm, A)

  train_data, a, b = minmax(train_data)
  test_data        = test_data * a + b
  return train_data, test_data

def ica_tranformer(train_data, test_data, train_labels, n_components):
  train_data, test_data = clean_normalized_feature_selection(train_data, test_data)
  ica=FastICA(n_components=n_components, random_state=0)
  ica.fit(train_data, train_labels)
  train_data = ica.transform(train_data)
  test_data = ica.transform(test_data)

  return train_data, test_data

def plsr_transformer(train_data, test_data, train_labels,n_components):
  train_data, test_data = clean_normalized_feature_selection(train_data, test_data)
  plsr = PLSRegression(n_components=n_components)
  plsr.fit(train_data, train_labels)
  train_data = plsr.transform(train_data)
  test_data = plsr.transform(test_data)

  return train_data, test_data

#código de Domingo Mery
class KDEClassifier(BaseEstimator, ClassifierMixin):
    """Bayesian generative classification based on KDE
    from https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html

    Parameters
    ----------
    bandwidth : float
        the kernel bandwidth within each class
    kernel : str
        the kernel name, passed to KernelDensity
    """
    def __init__(self, bandwidth=1.0, kernel='gaussian'):
        self.bandwidth = bandwidth
        self.kernel = kernel

    def fit(self, X, y):
        self.classes_ = np.sort(np.unique(y))
        training_sets = [X[y == yi] for yi in self.classes_]
        self.models_ = [KernelDensity(bandwidth=self.bandwidth,
                                      kernel=self.kernel).fit(Xi)
                        for Xi in training_sets]
        self.logpriors_ = [np.log(Xi.shape[0] / X.shape[0])
                           for Xi in training_sets]
        return self

    def predict_proba(self, X):
        logprobs = np.array([model.score_samples(X)
                             for model in self.models_]).T
        result = np.exp(logprobs + self.logpriors_)
        return result / result.sum(1, keepdims=True)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), 1)]

def create_classifiers():
    return {
    'knn                               ': KNeighborsClassifier(n_neighbors=1),
    'knn-3                             ': KNeighborsClassifier(n_neighbors=3),
    'knn-5                             ': KNeighborsClassifier(n_neighbors=5),
    'knn-8                             ': KNeighborsClassifier(n_neighbors=8),
    'knn-9                             ': KNeighborsClassifier(n_neighbors=9),
    'knn-10                            ': KNeighborsClassifier(n_neighbors=10),
    'knn-15                            ': KNeighborsClassifier(n_neighbors=15),
    'knn-20                            ': KNeighborsClassifier(n_neighbors=15),
    'mlp                               ': MLPClassifier(alpha=1, max_iter=1000, random_state=42),
    'mlp layers 2                      ': MLPClassifier(hidden_layer_sizes=(100, 50), alpha=1, max_iter=1000, random_state=42),
    'svm lineal 1                      ': SVC(kernel='linear', gamma=0.2, C=0.1),
    'svm lineal 2                      ': SVC(kernel='linear', gamma=0.25, C=0.2),
    'svm polinomial                    ': SVC(kernel='poly', gamma=0.2,degree=3, C=0.1),
    'svm rbf 1                         ': SVC(kernel='rbf', gamma=0.2, C=0.1),
    'svm rbf 2                         ': SVC(kernel='rbf', gamma=0.65, C=0.25),
    'svm rbf 3                         ': SVC(kernel="rbf", random_state=42),
    'svm rbf gamma auto                ': SVC(kernel='rbf', gamma='auto'),
    'svm sigmoidal                     ': SVC(kernel='sigmoid', gamma=0.01, C=1.5),
    'dmin                              ': NearestCentroid(),
    'bayes kde                         ': KDEClassifier(bandwidth=1.0),
    'naive bayes                       ': GaussianNB(),
    'lda                               ': LinearDiscriminantAnalysis(),
    'qda                               ': QuadraticDiscriminantAnalysis(),
    'random forest depth 3             ': RandomForestClassifier(max_depth=3,n_estimators=150),
    'random forest depth 15            ': RandomForestClassifier(max_depth=15,n_estimators=150),
    'random forest depth 30            ': RandomForestClassifier(max_depth=30, n_estimators=200),
    'random forest depth 100           ': RandomForestClassifier(max_depth=100,n_estimators=150),
    'random forest n_estimators 300    ': RandomForestClassifier(n_estimators=300),
    'decision tree                     ': DecisionTreeClassifier(max_depth=3),
    'decision tree depth 12            ': DecisionTreeClassifier(max_depth=12),
    'decision tree depth 100           ': DecisionTreeClassifier(max_depth=100),
    'logistic regression lbfgs         ': LogisticRegression(C=0.1,solver="lbfgs"),
    'logistic regression newton-cg     ': LogisticRegression(C=0.2,solver="newton-cg"),
    'gradient boosting                 ': GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=42),
    'adaboost                          ': AdaBoostClassifier(n_estimators=100),
    'extra trees                       ': ExtraTreesClassifier(n_estimators=100),
    'bagging                           ': BaggingClassifier(n_estimators=50),
    'perceptron                        ': Perceptron(max_iter=1000),
    'sgd                               ': SGDClassifier(max_iter=1000, tol=1e-3)
    }

def clasificacion(model, train_data, train_labels, test_data):
    model.fit(train_data, train_labels) #Se clasifica el Testing
    y_pred = model.predict(test_data)  #Se calcula el Accuracy en el Testing y se almacena en acc[i]
    return y_pred

def crossval(clf,X,y,nfolds=10,show=1):
  scores = cross_val_score(clf, X, y, cv=nfolds)
  acc = np.mean(scores)
  if show:
    acc_st = "{:.2f}".format(acc*100)
    print('Accuracy = '+str(acc_st))
  return acc

def evaluate_classifiers(classifiers, features, labels, nfolds=10, use_sfs=False,n_features=20):
    if use_sfs:
        sfs_indices = sfs(features, labels, n_features)
        features = features[:, sfs_indices]
        print(f'Selected Features: {sfs_indices}')

    accuracies = {}
    for name, clf in classifiers.items():
        print(f"\nEvaluando: {name.strip()}")
        accuracies[name] = crossval(clf, features, labels, nfolds=nfolds, show=1)
    
    print("\nPrecisión total por clasificador:")
    for name, acc in accuracies.items():
        print(f'{name.strip()}: {acc:.2f}')
    
    return accuracies

def print_accuracies(accuracies):
    print("\nAccuracy Total por Clasificador:")
    for name, acc in accuracies.items():
        print(f"{name}: {acc}")

def evaluate_model_cleannormalize(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = clean_normalized_feature_selection(train_data, test_data)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies

def evaluate_model_sfs5(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = sfs_selection(train_data, test_data, train_labels,5)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    return accuracies

def evaluate_model_sfs10(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = sfs_selection(train_data, test_data, train_labels,10)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_sfs15(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = sfs_selection(train_data, test_data, train_labels,15)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_sfs20(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = sfs_selection(train_data, test_data, train_labels,20)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_sfs25(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = sfs_selection(train_data, test_data, train_labels,25)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies

def evaluate_model_pca10(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = pca_tranformer(train_data, test_data,10)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_pca20(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = pca_tranformer(train_data, test_data,20)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_pca25(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = pca_tranformer(train_data, test_data,25)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies

def evaluate_model_ica10(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = ica_tranformer(train_data, test_data, train_labels,10)

   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_ica20(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = ica_tranformer(train_data, test_data, train_labels,20)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_ica25(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = ica_tranformer(train_data, test_data, train_labels,25)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies

def evaluate_model_plsr10(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = plsr_transformer(train_data, test_data, train_labels,10)

   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_plsr20(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = plsr_transformer(train_data, test_data, train_labels,20)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies
def evaluate_model_plsr25(train_data, test_data, train_labels, test_labels, classifiers):
    accuracies = {name: [] for name in classifiers.keys()}
    train_data, test_data = plsr_transformer(train_data, test_data, train_labels,25)
   
    for name, clf in classifiers.items():
        ypred = clasificacion(clf, train_data, train_labels, test_data)
        accuracy = accuracy_score(test_labels, ypred)
        accuracies[name].append(accuracy)
    
    return accuracies