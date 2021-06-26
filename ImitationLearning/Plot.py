import matplotlib.pyplot as plt
import pandas as pd


class Plot:
    def __init__(self, input_list, output_list):
        self.df1 = pd.DataFrame(input_list)  # x1, y1, x2, y2, x3, y3 .. ...
        self.df2 = pd.DataFrame(output_list)  # theta1, theta 2 ....
        self.X_train = self.df1.iloc[:,:].values
        self.y_train = self.df2.iloc[:,:].values

    def plot_2link_data(self):
        """
        Plots first 100 input data points
        :return:
        """
        plt.scatter(self.X_train[:100,0], self.X_train[:100,1])
        plt.scatter(self.X_train[:100,2], self.X_train[:100,3])

    def plot_2link_labels(self):
        """
        Plots first 100 target values
        :return:
        """

        plt.scatter(range(100),self.y_train[:100,0])
        plt.scatter(range(100),self.y_train[:100,1])

    def plot_3link_data(self):
        """
        Plots first 100 input data points
        :return:
        """
        plt.scatter(self.X_train[:100,0], self.X_train[:100,1])
        plt.scatter(self.X_train[:100,2], self.X_train[:100,3])
        plt.scatter(self.X_train[:100,4], self.X_train[:100,5])

    def plot_3link_labels(self):
        """
        Plots first 100 target values
        :return:
        """

        plt.scatter(range(100),self.y_train[:100,0])
        plt.scatter(range(100),self.y_train[:100,1])
        plt.scatter(range(100),self.y_train[:100,2])

    @staticmethod
    def plot_3link_validation(y, prediction, epoch = 0):
        fig = plt.figure()
        plt.scatter(y[:,0],prediction.to('cpu')[:,0])
        plt.scatter(y[:,1],prediction.to('cpu')[:,1])
        plt.scatter(y[:,2],prediction.to('cpu')[:,2])
        fig.savefig("theta1_iter"+str(epoch), dpi=300)
        plt.xlabel("Ground truth")
        plt.ylabel("Prediction")
        plt.show()

    @staticmethod
    def plot_2link_validation(y, prediction, epoch=0):
        fig = plt.figure()
        plt.scatter(y[:,0],prediction.to('cpu')[:,0])
        plt.scatter(y[:,1],prediction.to('cpu')[:,1])
        fig.savefig("theta1_iter"+str(epoch), dpi=300)
        plt.xlabel("Ground truth")
        plt.ylabel("Prediction")
        plt.show()