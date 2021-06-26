###########################################################
# Agents.py                                               #
# Defines templated class that needs to be inherited from #
# @author Gautam Sharma                                   #
###########################################################

__author__ = "Gautam Sharma"


from abc import ABC, abstractmethod


class Agent(ABC):
    """
    Template for defining a Reinforcement Learning agent
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_state(self, *args, **kwargs):
        """

        :param args: Any
        :param kwargs: Any
        :return: state defined as input for the RL algorithm
        """
        pass

    @abstractmethod
    def reset(self, *args, **kwargs):
        """
        Resets the environment
        :param args: Any
        :param kwargs: Any
        :return:
        """
        pass

    @abstractmethod
    def step(self, *args, **kwargs):
        """
        Usually implemented as:
        step(action)

        :param args: Any (usually action)
        :param kwargs: Any
        :return: self.get_state(), reward, done
        """
        pass

    @abstractmethod
    def terminate(self, *args, **kwargs):
        """
        Defines conditions to terminate the episode

        :param args:
        :param kwargs:
        :return: None
        """
        pass

    @abstractmethod
    def graphics(self, *args, **kwargs):
        pass

    @abstractmethod
    def take_action(self, *args, **kwargs):
        pass

    @staticmethod
    def log_data(*args, **kwargs):
        pass
