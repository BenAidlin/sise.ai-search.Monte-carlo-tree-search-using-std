# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in 
# the UCTPlayGame() function at the bottom of the code.
# 
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
import random

#Imprt the game specifications
from Othello import OthelloState
from Nim import NimState
from OXO import OXOState
from Connect4 import C4State
from collections import Counter

class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """
    def __init__(self):
            self.playerJustMoved = 2 # At the root pretend the player just moved is player 2 - player 1 has the first move
        
    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        self.playerJustMoved = 3 - self.playerJustMoved
        
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        self.rollouts_counter = Counter()
        self.last_rollout_res = None
        
    def UCTSelectChild(self, selection_function, w):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: (1-w)*(c.wins/c.visits + sqrt(2*log(self.visits)/c.visits)) + w*selection_function(c))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result
        self.rollouts_counter[result] += 1
        self.last_rollout_res = result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose = False, selected_std_function=lambda c: 0, std_weight=0):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild(selection_function=selected_std_function, w=std_weight)
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            state.DoMove(m)
            node = node.AddChild(m,state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose): print(rootnode.TreeToString(0))
    else: print(rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
                
def UCTPlayGame(state=None, player1_uct_iter=50, player2_uct_iter=50, uct_verbosity=False, std_weight=0, selected_std_function=lambda c: 0):
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    if(not state): state = C4State()
    while (state.GetMoves() != []):
        print(str(state))
        if state.playerJustMoved == 1:
            m = UCT(rootstate = state, itermax = player1_uct_iter, verbose = uct_verbosity) # player 2 moves
        else:
            m = UCT(rootstate = state, itermax = player2_uct_iter, verbose = uct_verbosity, 
                    selected_std_function=selected_std_function, std_weight=std_weight) # player 1 moves, and gets std addition
        print("Best Move: " + str(m) + "\n")
        state.DoMove(m)
    to_return = None
    if state.GetResult(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
        to_return = state.playerJustMoved
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
        to_return = 3 - state.playerJustMoved
    else: 
        print("Nobody wins!")
        to_return = 1.5
    print(state)
    return to_return

def regular_std(node):
    c = node.rollouts_counter
    n = node.visits
    mean = sum([k*v for k, v in c.items()])/n
    std = 0
    for k, v in c.items():
        std += v*((k-mean)**2)
    std = sqrt(std/n)
    return std

def last_res_std(node):
    c = node.rollouts_counter
    n = node.visits
    mean = sum([k*v for k, v in c.items()])/n
    std = abs(mean - node.last_rollout_res)
    return std

def get_game_instance(name, params_list):
    if name == 'nim':
        return NimState(params_list[0])
    elif name == 'c4':
        return C4State()
    elif name == 'xo':
        return OXOState()
    else:
        return OthelloState(params_list[0])

if __name__ == "__main__":
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    # state = NimState(150) # uncomment to play Nim with the given number of starting chips
    #  state = C4State()   #Uncomment to simulate a full game of connect 4
    std_w = [0.5, 0.2, 0.1, 0.05, 0.03, 0.01, 0]
    std_funcs = [regular_std, last_res_std]
    val_1_list = [15, 25, 50, 100]
    val_2_list = [15, 50, 25, 200]
    nim_d_dict = {'iter_1_vals': val_1_list,
                  'iter_2_vals': val_2_list,
                  'std_w': std_w,
                  'std_funcs': std_funcs,
                  'param': [15, 50, 100, 150, 1000]}
    c4_d_dict = {'iter_1_vals': val_1_list,
                'iter_2_vals': val_2_list,
                'std_w': std_w,
                'std_funcs': std_funcs,
                'param': [None]}
    xo_d_dict = {'iter_1_vals': val_1_list,
                'iter_2_vals': val_2_list,
                'std_w': std_w,
                'std_funcs': std_funcs,
                'param': [None]}
    ot_d_dict = {'iter_1_vals': val_1_list,
                'iter_2_vals': val_2_list,
                'std_w': std_w,
                'std_funcs': std_funcs,
                'param': [4,8]}
    games_details = {'nim': nim_d_dict, 'c4': c4_d_dict, 'xo': xo_d_dict, 'ot': ot_d_dict}
    for game_name, details in games_details.items():
        for w in details['std_w']:
            for func in details['std_funcs']:
                for i in range(len(details['iter_1_vals'])):
                    for param in details['param']:
                        results_C4_50_50 = []
                        iter_1 = details['iter_1_vals'][i]
                        iter_2 = details['iter_2_vals'][i]
                        std_weight = w
                        std_func = func
                        verbosity = False
                        for _ in range(100):
                            state = get_game_instance(game_name, param)
                            print(f'iteration number {_}')
                            results_C4_50_50.append(
                                UCTPlayGame(state=state, player1_uct_iter=iter_1, player2_uct_iter=iter_2, uct_verbosity=verbosity,
                                            std_weight=std_weight, selected_std_function=std_func))
                        results_C4_50_50_mean = sum(results_C4_50_50) / len(results_C4_50_50)
                        results_C4_50_50_std = sqrt(sum([(result - results_C4_50_50_mean)**2 for result in results_C4_50_50]) / len(results_C4_50_50))
                        with open('./results.txt', 'a') as f:
                            f.write(f'GAME: {game_name}')
                            f.write(f'iter details: std_w-{w}, std_func-{func.__name__}, func_param-{param}, iter1-{iter_1}, iter2-{iter_2}')
                            f.write(f'results_C4_50_50: {results_C4_50_50}')
                            f.write(f'results_C4_50_50_mean: {results_C4_50_50_mean}')
                            f.write(f'results_C4_50_50_std: {results_C4_50_50_std}')
                            f.write('******************************')
        with open('./results.txt', 'a') as f:
            f.write('-----------------------------------------------------------------------------')

            
                          
            

