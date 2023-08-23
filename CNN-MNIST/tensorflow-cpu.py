# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""

# %% Import functions for MNIST dataset
# Credit for import functions: https://stackoverflow.com/questions/39969045
import gzip
import struct
import numpy as np

def load_dataset(path_dataset):       
   with gzip.open(path_dataset,'rb') as f:
     magic, size = struct.unpack(">II", f.read(8))
     nrows, ncols = struct.unpack(">II", f.read(8))
     data = np.frombuffer(f.read(), dtype=np.dtype(np.uint8).newbyteorder('>'))
     data = data.reshape((size, nrows, ncols))
     return data

def load_label(path_label):
  with gzip.open(path_label,'rb') as f:
    magic, size = struct.unpack('>II', f.read(8))
    label = np.frombuffer(f.read(), dtype=np.dtype(np.uint8).newbyteorder('>'))
    return label

# %% Import datasets and normalize, 
import os
script_path = "D:\Repository\cnn-labelling\CNN-MNIST"
import_path = os.path.realpath(script_path) + '\dataset'

from keras.utils import to_categorical
X_train = load_dataset(import_path + '\\' + 'train-images-idx3-ubyte.gz') / 255.0
Y_train = load_label(import_path + '\\' + 'train-labels-idx1-ubyte.gz')
Y_train = to_categorical(Y_train)

X_test = load_dataset(import_path + '\\' + 't10k-images-idx3-ubyte.gz') / 255.0
Y_test = load_label(import_path + '\\' + 't10k-labels-idx1-ubyte.gz')
Y_test = to_categorical(Y_test)
print("Data imported.")

# %% Visualize the first few image if needed
"""
import matplotlib.pyplot as plt
for i in range(1, 10):
    plt.imshow(X_train[i,:,:], cmap='gray')
    plt.show()
"""

# %% Model training
import tensorflow as tf

with tf.device('/CPU:0'):
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),    
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(10, activation='softmax')])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=5)
    print("Model trained.")

# %% Model prediction
boolean = 'Y'
print("Write a number in MS Paint.")

while boolean == 'Y' or boolean == 'y':
    
    from PIL import Image
    image = Image.new('L', (28, 28), color=0)
    image_path = 'temp_image.png'
    image.save(image_path)

    import subprocess
    process = subprocess.Popen(['mspaint', image_path])
    process.wait()

    modified_image = Image.open(image_path)
    modified_image = modified_image.convert('L')
    modified_image = np.array(modified_image)
    modified_image = modified_image.reshape(-1, 28, 28, 1)

    import os
    os.remove(image_path)
    
    with tf.device('/CPU:0'): predictions = model.predict(modified_image)
    index = np.argmax(predictions)
    value = predictions[0, index]

    print('According to the prediction of the trained model,')
    print('the given number is', index, 'with a', value*100, '% confidence.')
    print()
    
    boolean = input("Do you want to write another number? (Y/N)")