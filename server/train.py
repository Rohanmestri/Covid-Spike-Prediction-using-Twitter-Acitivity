import pandas as pd
import numpy as np
import os
import sys
from textprep import text_prep
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Input
from tensorflow.keras.utils import to_categorical
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score,f1_score,confusion_matrix
from tensorflow.keras.layers import Dense, Input, LSTM, Embedding, Dropout, Activation,Lambda
from gensim.models import FastText
import json
import pickle
import tensorflow as tf
#import tensorflow.compat.v1 as tf
#tf.disable_eager_execution()
tf.compat.v1.disable_eager_execution()
tf.compat.v1.experimental.output_all_intermediates(True)
#from tensorflow.python.framework.tensor_shape import Dimension
import tensorflow_hub as hub

dataset1 = pd.read_excel("tweets3.xlsx")
dataset2 = pd.read_excel("tweets4.xlsx")

dataset=pd.concat([dataset1,dataset2],axis=0)

dataset=dataset[['Text','GT']]
dataset.columns=['sentence','label']

dataset.sentence = dataset.sentence.apply(lambda x: text_prep(x))

dataset.dropna(inplace=True, axis=0)

dataset['label']=dataset['label'].apply(lambda x: str(x).lower())

dataset = dataset.sample(frac = 1)

y_train = list(dataset['label'])
x_train = list(dataset['sentence'])


lb = preprocessing.LabelEncoder()
lb.fit(y_train)
pickle.dump(lb, open('LabelEncoder.pkl', 'wb'))

def encd(lb, labels):
    enc = lb.transform(labels)
    return to_categorical(enc)

def decd(lb, one_hot):
    dec = np.argmax(one_hot, axis=1)
    return lb.inverse_transform(dec)

y_train = encd(lb, y_train)

x_train = np.asarray(x_train)
y_train = np.asarray(y_train)


#model training
url = "https://tfhub.dev/google/elmo/2"
embed = hub.Module(url)

def elmoembd(x):
    return embed(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["default"]


input_text = Input(shape=(1,), dtype=tf.string)
embedding = Lambda(elmoembd, output_shape=(1024, ))(input_text)
dense1 = Dense(128, activation='relu')(embedding)
dense2= Dropout(0.5)(dense1)
dense3 = Dense(256, activation='relu')(dense2)
dense4= Dropout(0.3)(dense3)
pred = Dense(2, activation='softmax')(dense4)
model = Model(inputs=[input_text], outputs=pred)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

with tf.compat.v1.Session() as session:
    tf.compat.v1.keras.backend.set_session(session)
    session.run(tf.compat.v1.global_variables_initializer())
    session.run(tf.compat.v1.tables_initializer())
    history = model.fit(x_train, y_train, epochs=5, batch_size=32,verbose=1, validation_split=0.2)
    model_json = model.to_json()
    with open("elmomodel.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("elmo_model.h5")

print("Training Done")
print("Model Saved")
