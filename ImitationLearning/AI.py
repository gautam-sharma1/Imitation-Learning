import os
import random
from abc import ABC, abstractmethod

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class Algorithm(ABC):
    """
    Abstract class.
    """

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return self.__name__()

    @abstractmethod
    def act(self, state):
        pass

    @abstractmethod
    def compute_single_loss(self, state, action, reward, next_state, done):
        pass

    @abstractmethod
    def compute_batch_loss(self, state, action, reward, next_state, done):
        pass

    @abstractmethod
    def save_model(self, PATH='./models/'):
        pass

    @staticmethod
    def tuple_to_tensor(input):
        l = []
        for i in input:
            l.append([i])
        return torch.FloatTensor(l)


# TODO:
class DDPG:
    pass


# TODO:
class PPO:
    pass


class DQN(Algorithm):
    """
        Deep Q-Networks Algorithm
    """
    def __init__(self, epsilon, input_dim, output_dim, optimizer='Adam', loss_fcn=nn.MSELoss()):
        super().__init__()
        self.epsilon = epsilon
        self.optim = optim
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.actor = Net(input_dim, output_dim)
        self.critic = Net(input_dim, output_dim)
        self.critic.load_state_dict(self.actor.state_dict())
        self.optimizer = optim.Adam(self.actor.parameters(),lr=0.0001)
        self.n_games = 0
        self.gamma = 0.9
        self.criterion = loss_fcn

    def act(self, state):
        if random.random() > self.epsilon:
            output = self.actor(state)
            return torch.argmax(output)
        else:
            return random.randint(0, self.output_dim - 1)

    def copy_weights(self):
        self.critic.load_state_dict(self.actor.state_dict())

    def compute_batch_loss(self, state, action, reward, next_state, done):

        state = torch.vstack(state)
        next_state = torch.vstack(next_state)
        t_action = self.tuple_to_tensor(action)
        t_action = torch.tensor(t_action, dtype=torch.int64).clone().detach()
        t_reward = self.tuple_to_tensor(reward)
        t_done = self.tuple_to_tensor(done)
        q_values = self.actor(state)
        next_q_values = self.critic(next_state)
        q_value = q_values.gather(1, t_action)
        next_q_value = next_q_values.max(1)[0]
        # next_q_value = next_q_value.view(-1,1)  # extra for DQN for images
        expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done)
        # loss = self.criterion(q_value, expected_q_value)
        loss = (q_value - expected_q_value.data).pow(2).mean()
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss

    def compute_single_loss(self, state, action, reward, next_state, done):

        t_reward = torch.tensor(reward, dtype=torch.float16)
        t_done = torch.tensor(done, dtype=torch.int)
        q_values = self.actor(state)
        next_q_values = self.critic(next_state)
        q_value = q_values[action].view(1)
        next_q_value = next_q_values.max().item()
        expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done)
        loss = self.criterion(q_value, expected_q_value)
        # loss = (q_value - expected_q_value.data).pow(2).mean()
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss

    def save_model(self, PATH='./models/net.pth'):
        if not os.path.exists('models'):
            os.makedirs('models')
        torch.save(self.actor.state_dict(), PATH)


class DQL(Algorithm):  # width, height, output
    def __init__(self, epsilon, input_dim, output_dim, optimizer='Adam', loss_fcn=nn.MSELoss()):
        super().__init__()
        self.epsilon = epsilon
        self.optim = optim
        self.n_games = 0
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.model = Net(input_dim, output_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)
        self.criterion = loss_fcn
        self.gamma = 0.9

    def act(self, state):
        self.epsilon = 80 - self.n_games

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, self.output_dim - 1)
            final_move = move
        else:
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
            final_move = move

        return final_move

    def save_model(self, PATH='./models/net.pth'):
        if not os.path.exists('models'):
            os.makedirs('models')
        torch.save(self.model.state_dict(), PATH)

    # # Extra
    # def compute_single_loss(self,state, action, reward, next_state, done):
    #
    #     # state, action, reward, next_state, done #= zip(*replay_buffer.get_random())
    #
    #     t_action = torch.tensor(action)
    #     t_reward = torch.tensor(reward)
    #     t_done  = torch.tensor(done,dtype = int)
    #
    #     pred = self.model(state)
    #     q_values = self.model(state)
    #     target = pred.clone()
    #
    #     next_q_values = self.model(next_state)
    #
    #     q_value = (q_values * t_action)
    #
    #     q_value = torch.sum(q_value)
    #
    #     next_q_value = next_q_values.max().item()
    #
    #     expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done)
    #     loss = (q_value - expected_q_value.data).pow(2).mean()
    #
    #     self.optimizer.zero_grad()
    #     loss.backward()
    #     self.optimizer.step()
    #
    #     return loss
    #
    def compute_batch_loss(self, state, action, reward, next_state, done):

        state = torch.vstack(state)
        next_state = torch.vstack(next_state)
        t_action = self.tuple_to_tensor(action)
        t_action = torch.tensor(t_action, dtype=torch.int64).clone().detach()
        t_reward = self.tuple_to_tensor(reward)
        t_done = self.tuple_to_tensor(done)
        q_values = self.model(state)
        next_q_values = self.model(next_state)
        q_value = q_values.gather(1, t_action).view(-1,1)
        next_q_value = next_q_values.max(1)[0]
        next_q_value = next_q_value.view(-1,1)  # extra for DQN for images
        expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done).view(-1,1)
        loss = self.criterion(q_value, expected_q_value)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss

    def compute_single_loss(self, state, action, reward, next_state, done):

        t_reward = torch.tensor(reward, dtype=torch.float16)
        t_done = torch.tensor(done, dtype=torch.int)
        q_values = self.model(state)
        next_q_values = self.model(next_state)
        q_value = q_values[action].view(-1,1)
        next_q_value = next_q_values.max().item()
        expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done).view(-1,1)
        loss = self.criterion(q_value, expected_q_value)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss

    # # Extra
    # def compute_batch_loss(self, state, action, reward, next_state, done):
    #
    #         # with torch.no_grad():
    #         state = torch.vstack(state)
    #         next_state = torch.vstack(next_state)
    #         t_action = self.tuple_to_tensor(action)
    #         t_action = torch.squeeze(t_action,1)
    #         t_reward = self.tuple_to_tensor(reward)
    #         t_done = self.tuple_to_tensor(done)
    #         pred = self.model(state)
    #         q_values = self.model(state)
    #         target = pred.clone()
    #         next_q_values = self.model(next_state)
    #         q_value = (q_values*t_action)
    #         q_value = torch.sum(q_value,dim = 1)
    #         #print(q_value)
    #         #q_value = q_values.gather(1, torch.argmax(t_action[:]))
    #         next_q_value = next_q_values.max(1)[0]
    #         expected_q_value = t_reward + self.gamma * next_q_value * (torch.LongTensor([1]) - t_done)
    #         loss = (q_value - expected_q_value.data).pow(2).mean()
    #         self.optimizer.zero_grad()
    #         loss.backward()
    #         self.optimizer.step()
    #
    #         return loss


class Net(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(Net, self).__init__()
        self.linear1 = nn.Linear(input_dim, 32)
        self.linear2 = nn.Linear(32, 32)
        self.linear3 = nn.Linear(32, 64)
        self.linear4 = nn.Linear(64, output_dim)


    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        x = self.linear4(x)
        return x


class Net32(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(Net32, self).__init__()
        self.linear1 = nn.Linear(input_dim, 32)
        self.linear2 = nn.Linear(32, output_dim)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x


class Net16(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(Net16, self).__init__()
        self.linear1 = nn.Linear(input_dim, 16)
        self.linear2 = nn.Linear(16, output_dim)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x


class NNet(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(NNet, self).__init__()
        self.linear1 = nn.Linear(input_dim, 64)
        self.linear2 = nn.Linear(64, 256)
        self.linear3 = nn.Linear(256, output_dim)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x


class Temp(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(Temp, self).__init__()
        self.linear1 = nn.Linear(input_dim, 256)
        self.linear2 = nn.Linear(256, 256)
        self.linear3 = nn.Linear(256, 256)
        self.linear4 = nn.Linear(256, output_dim)

    def forward(self, x):
        x = F.leaky_relu(self.linear1(x))
        x = F.sigmoid(self.linear2(x))
        x = F.leaky_relu(self.linear3(x))
        x = self.linear4(x)
        return x


class Netleaky(nn.Module):  # TODO improve the class definition
    def __init__(self, input_dim, output_dim):
        super(Netleaky, self).__init__()
        self.linear1 = nn.Linear(input_dim, 32)
        self.linear2 = nn.Linear(32, 32)
        self.linear3 = nn.Linear(32, 64)
        self.linear4 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        x = self.linear4(x)
        return x