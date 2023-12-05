# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
try:
    # Import core libraries
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    import torchvision.transforms as transforms

    # Import libraries for utilities
    import os, time, random, subprocess
    import matplotlib.pyplot as plt
    from PIL import Image
    from torch.utils.data import DataLoader
    from torchvision.datasets import EMNIST
    from colorama import init, Fore
    init()
    print(Fore.GREEN + "All libraries imported.")

except:
    print("Dependencies missing, please use pip to install all dependencies:")
    print("torch, torchvision, os, time, random, subprocess, matplotlib, PIL, colorama")
    input('Press any key to quit.')
    exit()
    
# %% Load MNIST data into system memory
directory = os.path.dirname(os.path.realpath(__file__))

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])

dataset_train = EMNIST(root=directory, split="bymerge", train=True, transform=transform, download=True)
dataset_test = EMNIST(root=directory, split="bymerge", train=False, transform=transform, download=True)

"""
By Merge: This data hierarchy addresses an interesting problem in the classification of handwritten digits, which
is the similarity between certain uppercase and lowercase letters. Indeed, these effects are often plainly visible when
examining the confusion matrix resulting from the full classification task on the By Class dataset. This variant
on the dataset merges certain classes, creating a 47-class classification task. The merged classes, as suggested by
the NIST, are for the letters C, I, J, K, L, M, O, P, S, U, V, W, X, Y and Z."

source: https://arxiv.org/pdf/1702.05373v1.pdf
"""
dictionary = {0:"0  ", 1:"1  ", 2:"2  ", 3:"3  ", 4:"4  ", 5:"5  ", 6:"6  ", 7:"7  ", 8:"8  ", 9:"9  ",
              10:"A  ", 11:"B  ", 12:"C/c", 13:"D  ", 14:"E  ", 15:"F  ", 16:"G  ", 17:"H  ", 18:"I/i",
              19:"J/j", 20:"K/k", 21:"L/l", 22:"M/m", 23:"N  ", 24:"O/o", 25:"P/p", 26:"Q  ", 27:"R  ",
              28:"S/s", 29:"T  ", 30:"U/u", 31:"V/v", 32:"W/w", 33:"X/x", 34:"Y/y", 35:"Z/z", 36:"a  ",
              37:"b  ", 38:"d  ", 39:"e  ", 40:"f  ", 41:"g  ", 42:"h  ", 43:"n  ", 44:"q  ", 45:"r  ", 46:"t  "}

loader_train = DataLoader(dataset=dataset_train, batch_size=256, shuffle=True)
loader_test = DataLoader(dataset=dataset_test, batch_size=256, shuffle=True)

print(Fore.WHITE + "EMNIST dataset loaded.")

# %% Visualization of random samples
visualize = True
if visualize:
    index, fig = 0, plt.figure(figsize=(5, 5))
    for i in [random.randint(0, len(dataset_train)-1) for j in range(25)]:
        index += 1
        fig.add_subplot(5, 5, index)
        plt.xticks([])
        plt.yticks([])
        
        image_slice = dataset_train[i][0].numpy()
        plt.imshow(image_slice[0].transpose())            
    print(Fore.WHITE + "Visualizing 25 random samples, close the image to continue...")
    plt.show()    
del visualize, i, index, fig, image_slice, dataset_test, dataset_train

# %% Initialize CNN model

# ### Kernel Size / Stride / Padding ###
# Kernel size determine the size of the filter, which is usually an odd integer.
# - If the input size is a*b and the kernel size is 2n+1,
# - then the output size will be (a-2n)*(b-2n) assuming a,b greater than 2n.
# Stride determine how fast (how many pixel at a time) the filter will move horizontally and vertically.
# Padding determine how many pixels the original image should extend at the border.

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=4, kernel_size=5, stride=1, padding=0)
        self.conv2 = nn.Conv2d(in_channels=4, out_channels=16, kernel_size=5, stride=1, padding=0)
        self.fc1 = nn.Linear(in_features=16*20*20, out_features=400)
        self.fc2 = nn.Linear(in_features=400, out_features=100)
        self.fc3 = nn.Linear(in_features=100, out_features=47)

    def forward(self, x):
        x = nn.functional.relu(self.conv1(x))
        x = nn.functional.relu(self.conv2(x))
        x = x.view(-1, 16*20*20)
        x = nn.functional.relu(self.fc1(x))
        x = nn.functional.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = CNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
print(Fore.WHITE + "CNN Model Initialized.")

# %% Model training
def train_model(loader, model) -> nn.Module:
    start_time = time.time()
    for epoch in range(5):
        running_loss = 0.0
        for i, data in enumerate(loader, 0):
            inputs, labels = data
            inputs = inputs
            labels = labels

            scores = model(inputs)
            loss = criterion(scores, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()      
            if i % 100 == 99:
                average_loss = running_loss / 100
                print(f"Epoch {epoch+1}, Batch {i+1}, Loss: {average_loss:.3f}")

    end_time = time.time()
    total_time = end_time - start_time
    print(Fore.GREEN + f"Total training time: {total_time:.2f} seconds")
    return model

# %% Main Execution
if not os.path.isfile(directory + '/pre_trained_model.pt'):
    print(Fore.WHITE + "No pre-trained model detected.")
    print(Fore.WHITE + "Start training...")
    model = train_model(loader_train, model)       
    torch.save(model.state_dict(), directory + '/pre_trained_model.pt')
    print(Fore.GREEN + "Model have been saved to the default location.")
else:
    print(Fore.GREEN + "Pre-trained model detected.")
    model.load_state_dict(torch.load(directory + '/pre_trained_model.pt', map_location=torch.device('cpu')))
    print(Fore.GREEN + "Pre-trained model loaded.")
    
# %% Model testing
def check_accuracy(loader, model) -> float:
    num_correct = 0
    num_samples = 0
    model.eval()

    with torch.no_grad():
        for x, y in loader:            
            scores = model(x)
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)

    accuracy = f"{num_correct/num_samples * 100:.2f}%"
    print(Fore.WHITE + "This model has a", accuracy, "accuracy on the test dataset.")
    return accuracy

check_accuracy(loader_test, model)

# %% Model prediction
boolean = 'Y'
print(Fore.WHITE + "Please write a character in MS Paint and save it.")

while boolean == 'Y' or boolean == 'y':

    image = Image.new('L', (28, 28), color=0)
    image_path = 'test_image.png'
    image.save(image_path)

    process = subprocess.Popen(['mspaint', image_path])
    process.wait()

    modified_image = Image.open(image_path)
    modified_image = modified_image.transpose(Image.TRANSPOSE)
    modified_image = modified_image.convert('L')
    modified_image = transform(modified_image)
    modified_image = modified_image.unsqueeze(0)

    with torch.no_grad():
        model.eval()
        output = model(modified_image)

    softmax_scores = F.softmax(output, dim=1)
    softmax_scores = softmax_scores.tolist()[0]
    softmax_scores = ["{:0>5.2f}%".format(score*100) for score in softmax_scores]
    
    print(Fore.WHITE + "Predicted character:")
    for i in range(0, 47):
        print(Fore.WHITE, dictionary[i], ":", softmax_scores[i])
    print("")
    del i, boolean, image_path, image, modified_image
    boolean = input(Fore.WHITE + "Do you want to write another character? (Y/N)")