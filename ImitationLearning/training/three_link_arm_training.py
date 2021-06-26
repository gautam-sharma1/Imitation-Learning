##################################################################
# three_link_arm_training.py                                     #
# Predicts inverse kinematics data from forward kinematics data #
# @author Gautam Sharma                                          #
##################################################################

__author__ = "Gautam Sharma"

import pickle
import torch
import torch.utils.data as Data
from ImitationLearning.Plot import Plot
from ImitationLearning.AI import Net as Net

with open('../files/3link_pendulum_input_new.pkl', 'rb') as f:
    input_list = pickle.load(f)


with open('../files/3link_pendulum_output_new.pkl', 'rb') as f:
    output_list = pickle.load(f)

p = Plot(input_list, output_list)
p.plot_3link_data()
p.plot_3link_labels()

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline


class Dataset(torch.utils.data.Dataset):
    'Characterizes a dataset for PyTorch'
    def __init__(self, input_list, labels):
        'Initialization'

        self.input = input_list   # x, y
        self.labels = labels  #torch.FloatTensor([a/90, b/90 for a,b in labels])     # theta

    def __len__(self):
        'Denotes the total number of samples'
        return len(self.input)

    def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        X = torch.FloatTensor(self.input[index])
        y = torch.tensor(self.labels[index], dtype=torch.float32)
        return X, y/90

use_cuda = torch.cuda.is_available()

device = torch.device("cuda:0" if use_cuda else "cpu")

# Parameters
params = {'batch_size':64 ,
          'shuffle': True}
max_epochs = 100

# Datasets
input_data = input_list

labels = output_list

# Generators
training_set = Dataset(input_list, output_list)

training_generator = torch.utils.data.DataLoader(training_set, **params)
PATH = '../models/three_link_arm_training'
# for 2 link net = Net(4,2)
net = Net(6,3)
net = net.to(device)
#net.load_state_dict(torch.load(PATH, map_location=torch.device('cpu')))
optimizer = torch.optim.Adam(net.parameters(), lr = 0.00001)
loss_func = torch.nn.MSELoss()  # this is for regression mean squared loss
loss = 0
min_loss = 100000
loss_list = []


# train the network
data = []

X = []
Y = []
Z = []

for t in range(50):
    for local_batch, local_labels in training_generator:

        local_batch, local_labels = local_batch.to(device), local_labels.to(device)

        prediction = net(local_batch)  # input x and predict based on x
        local_labels = local_labels.view(-1,1)
        prediction = prediction.view(-1,1)

        loss = loss_func(prediction, local_labels)  # must be (1. nn output, 2. target)
        if loss < min_loss:
            torch.save(net.state_dict(), PATH+str(t))
            min_loss = loss

        optimizer.zero_grad()  # clear gradients for next train
        loss.backward()  # backpropagation, compute gradients
        optimizer.step()  # apply gradients

    with torch.no_grad():
        x,y = next(iter(training_generator))
        prediction = net(x.to(device))
        p.plot_3link_validation(y,prediction,epoch=t)

    loss_list.append(loss)
    print(f"Episode #{t} : Loss {loss}")

# plt.plot(range(len(loss_list)), loss_list)
