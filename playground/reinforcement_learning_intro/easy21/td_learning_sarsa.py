"""TD Learning.
"""
import numpy as np
from matplotlib import cm
from tqdm import tqdm

import easy21_environment as easyEnv

import pdb

class SarsaAgent:

    def __init__(self, environment, num_episodes=1000, n0=100):
        self.env = environment
        self.num_episodes = num_episodes
        # This is a constant-hyperparameter.
        self.N0 = float(n0)

        self.Q = np.zeros((self.env.dealer_value_count,
                           self.env.player_value_count,
                           self.env.action_count))

        # N(s) is book-keeping for the number of times state
        # s has been visited. N(s,a) is the number of times
        # action a has been selected from state s.
        self.N = np.zeros((self.env.dealer_value_count,
                           self.env.player_value_count,
                           self.env.action_count))

        # Initialise the value function to zero.
        self.V = np.zeros((self.env.dealer_value_count,
                           self.env.player_value_count))

        self.player_wins = 0
        self.episodes = 0

    def get_epsilon(self, N):
        return self.N0 / (self.N0 + N)

    def epsilon_greedy_policy(self, state):
        """Epsilon-greedy exploration strategy.

        Args:
            state: State object representing the status of the game.

        Returns:
            action: Chosen action based on Epsilon-greedy.
        """
        dealer = state.dealer_sum - 1
        player = state.player_sum - 1
        epsilon = self.get_epsilon(sum(self.N[dealer, player, :]))
        if np.random.rand() < (epsilon):

            action = np.argmax(self.Q[dealer, player, :])
        else:
            action = np.random.choice(easyEnv.ACTIONS)

        return action

    def train(self):
        """TD-Sarsa training.
        """

        for episode in tqdm(range(self.num_episodes)):

            # Initialize the state
            state = self.env.init_state()

            while not state.terminal:
                action = self.epsilon_greedy_policy(state)

                # Book-keeping the visits
                next_state, reward = self.env.step(state, action)

                # Sarsa update
                idx = state.dealer_sum - 1, state.player_sum - 1, action
                self.N[idx] += 1
                alpha = 1.0 / self.N[idx]

                self.Q[idx] += alpha * (reward - self.Q[idx])

                state = next_state

            if reward == 1:
                self.player_wins += 1

        for d in range(self.env.dealer_value_count):
            for p in range(self.env.player_value_count):
                self.V[d, p] = max(self.Q[d, p, :])

    def plot_frame(self, ax):

        X = np.arange(0, self.env.dealer_value_count, 1)
        Y = np.arange(0, self.env.player_value_count, 1)
        X, Y = np.meshgrid(X, Y)
        Z = self.V[X, Y]
        surf = ax.plot_surface(
            X,
            Y,
            Z,
            rstride=1,
            cstride=1,
            cmap=cm.coolwarm,
            linewidth=0,
            antialiased=False)
        return surf
