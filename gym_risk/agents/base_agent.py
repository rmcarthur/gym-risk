

class BaseAgent():
    """
    A Base agent that has methods for making decisions
    """
    def __init__(self,id: int=0,color: str='blue'):
        self.id = id
        self.color = color
        pass

    def make_attack_decision(self,actions, *args):
        '''
        actions: A list of available actions

        Returns: An action to take
        '''
        raise NotImplementedError 

    def make_reinforce_decision(self,actions, *args):
        '''
        '''
        raise NotImplementedError