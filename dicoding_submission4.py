# -*- coding: utf-8 -*-
"""dicoding_submission4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jmC4aR1iwbQ1lZYhPkMABj9722pMDTQk

#Fajri Yanti 




> M03 - Proyek Akhir : Image Classification Model Deployment
"""

!wget https://download.microsoft.com/download/3/E/1/3E1C3F21-ECDB-4869-8368-6DEBA77B919F/kagglecatsanddogs_5340.zip

!unzip kagglecatsanddogs_5340.zip

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
import tqdm
import tensorflow as tf
import random
import tensorflow as tf
import pathlib
from keras.preprocessing.image import load_img
warnings.filterwarnings('ignore')

label = []
path_in = []


for class_pet in os.listdir("PetImages"):
    for path in os.listdir("PetImages/"+class_pet):
        if class_pet == 'Cat':
            label.append(0)
        else:
            label.append(1)
        path_in.append(os.path.join("PetImages", class_pet, path))
print(path_in[0], label[0])

data = pd.DataFrame()
data['images'] = path_in
data['label'] = label
data = data.sample(frac=1).reset_index(drop=True)
data.head()

data.info(verbose=True, null_counts=True)

for pet in data['images']:
    if '.jpg' not in pet:
        print(pet)

import PIL
pil = []
for image in data['images']:
    try:
        pict = PIL.Image.open(image)
    except:
        pil.append(image)
pil

data = data[data['images']!='PetImages/Dog/Thumbs.db']
data = data[data['images']!='PetImages/Cat/Thumbs.db']
data = data[data['images']!='PetImages/Cat/666.jpg']
data = data[data['images']!='PetImages/Dog/11702.jpg']
len(data)

plt.figure(figsize=(10,10))
temp = data[data['label']==0]['images']
start = random.randint(0, len(temp))
files = temp[start:start+25]

for index, file in enumerate(files):
    plt.subplot(5,5, index+1)
    pict = load_img(file)   
    pict = np.array(pict)
    plt.imshow(pict)
    plt.title('Cats')
    plt.axis('off')

plt.figure(figsize=(10,10))
temp = data[data['label']==1]['images']
start = random.randint(0, len(temp))
files = temp[start:start+25]

for index, file in enumerate(files):
    plt.subplot(5,5, index+1)
    pict = load_img(file)   
    pict = np.array(pict)
    plt.imshow(pict)
    plt.title('Dogs')
    plt.axis('off')

data['label'] = data['label'].astype('str')
data.head()

from sklearn.model_selection import train_test_split
train, test = train_test_split(data, test_size=0.2, random_state=42)

from keras.preprocessing.image import ImageDataGenerator
train_generator = ImageDataGenerator(
    rescale = 1./255,
    horizontal_flip = True,
    rotation_range = 40, 
    zoom_range = 0.2,
    shear_range = 0.2,
    fill_mode = 'nearest'
)

val_generator = ImageDataGenerator(rescale = 1./255)

traindata_gen = train_generator.flow_from_dataframe(
    train,x_col='images',
    y_col='label',
    target_size=(128,128),
    batch_size=512,
    class_mode='binary'
)

valdata_gen = val_generator.flow_from_dataframe(
    test,x_col='images',
    y_col='label',
    target_size=(128,128),
    batch_size=512,
    class_mode='binary'
)

from keras import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten, Dense

model = Sequential([
            Conv2D(16, (3,3), activation='relu', input_shape=(128,128,3)),
            MaxPool2D((2,2)),
            Conv2D(32, (3,3), activation='relu'),
            MaxPool2D((2,2)),
            Conv2D(64, (3,3), activation='relu'),
            MaxPool2D((2,2)),
            Flatten(),
            Dense(512, activation='relu'),
            Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

accuracy_threshold = 98e-2
class cb(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs = None):
        if logs.get('accuracy') >= accuracy_threshold:
            print('\nFor Epoch', epoch, '\nAccuracy has reach = %2.2f%%' %(logs['accuracy']*100), 'training has been stopped.')
            self.model.stop_training = True

history = model.fit(traindata_gen, epochs=10, validation_data=valdata_gen, callbacks = [cb()])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
epochs = range(len(acc))

plt.figure(figsize=(10, 7))
plt.plot(epochs, acc, 'b', label='Training')
plt.plot(epochs, val_acc, 'r', label='Validation')
plt.title('Accuracy')
plt.legend()
plt.figure()

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(10, 7))
plt.plot(epochs, loss, 'b', label='Training')
plt.plot(epochs, val_loss, 'r', label='Validation')
plt.title('Loss')
plt.legend()
plt.show()

# Menyimpan model dalam format SavedModel
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)
 
# Convert SavedModel menjadi vegs.tflite
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()
 
tflite_model_file = pathlib.Path('dogcat_imgclassification.tflite')
tflite_model_file.write_bytes(tflite_model)