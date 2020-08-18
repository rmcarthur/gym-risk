import random
import numpy as np

rng = np.random.default_rng()
sided_die = 6
attack_max = 3
defend_max = 2
attack_until_threshold = 2

def single_roll(attack, defend):
    attack_roll = np.sort(rng.integers(1,sided_die+1,min(attack_max,attack)))[::-1]
    defend_roll = np.sort(rng.integers(1,sided_die+1,min(defend_max,defend)))[::-1]
    max_loss = min(len(attack_roll), len(defend_roll))
    attack_wins = np.sum([i>j for i,j in zip(attack_roll,defend_roll)]) 
    new_attack = attack - max_loss - attack_wins
    new_defend = defend - attack_wins
    return new_attack, new_defend