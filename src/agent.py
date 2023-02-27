from collections import deque
from src.planegame import FlightGame
import numpy as np
import random
import torch 
from src.chartslib.plot_helper import plot, histogram
from src.deep_qlearning.model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

STATE_SIZE = 120

class Agent:
    def __init__(self, network_dimensions: tuple):
        # Game number
        self.n_game = 0
        
        # Stands for randomness in exploration / exploitation phase
        self.epsilon = 0 
        self.gamma = 0.9 # discount rate ???
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(*network_dimensions)
        self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)       
    
    def get_state(self, game: FlightGame):
        """Returns the state of the game.
        i.e. Position of the plane and positions of all the rockets.
        """
        state = game.radar.get_radar_states(game.enemies)
        return np.array(state, dtype=int).flatten()

    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done)) # popleft if memory exceed
    
    def train_long_memory(self):
        if (len(self.memory) > BATCH_SIZE):
            mini_sample = random.sample(self.memory,BATCH_SIZE)
        else:
            mini_sample = self.memory
        states,actions,rewards,next_states,dones = zip(*mini_sample)
        self.trainer.train_step(states,actions,rewards,next_states,dones)
    
    def train_short_memory(self,state,action,reward,next_state,done):
        state = np.array(state)
        self.trainer.train_step(state,action,reward,next_state,done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_game
        # Final moves: 
        # top-right | right | bottom-right
        # bottom | bottom-left | left 
        # top-left | top | stay
        
        final_move = 9*[0]
        if(random.randint(0,200)<self.epsilon):
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.flatten(torch.tensor(state, dtype=torch.float))
            prediction = self.model(state0) # predict move values by model
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move
    

def train():
    """
    Function resposible for visual training of ML model.
    Run it to see how does AI play the game and learns from its mistakes.
    """
    
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    network_dimensions = (STATE_SIZE, 256, 9)
        
    agent = Agent(network_dimensions)
    game = FlightGame()
        
    plt = None
    iteration_count = 0
    MAX_ITERATIONS = 150
    while iteration_count < MAX_ITERATIONS:
        # Get old state
        state_old = agent.get_state(game)
            
        # get move
        final_move = agent.get_action(state_old)
            
        #  perform move and get the new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
            
        # train short memory
        agent.train_short_memory(state_old,final_move,reward,state_new,done)
            
        #remember
        agent.remember(state_old,final_move,reward,state_new,done)
            
        if done:
            # Train long memory, plot the result
            game.reset()
            agent.n_game += 1
            print("training long memory")
            agent.train_long_memory()
            if(score > record): # new High score 
                record = score
                agent.model.save()
            print('Game:',agent.n_game,'Score:',score,'Record:',record)
                
            plot_scores.append(score)
            total_score+=score
            mean_score = total_score / agent.n_game
            plot_mean_scores.append(mean_score)
            plot(plot_scores,plot_mean_scores)
                
            iteration_count += 1