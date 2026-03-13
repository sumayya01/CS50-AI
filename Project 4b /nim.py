import random
import time


class Nim:
    def __init__(self, initial=[1, 3, 5, 7]):
        """
        Initialize the game with piles and starting player.
        """
        self.piles = initial.copy()
        self.player = 0  # Player 0 starts
        self.winner = None

    @staticmethod
    def available_actions(piles):
        """
        Return all possible moves (pile_index, count) for current piles.
        """
        actions = set()
        for i, pile in enumerate(piles):
            for count in range(1, pile + 1):
                actions.add((i, count))
        return actions

    @staticmethod
    def other_player(player):
        """
        Return the other player (0 or 1).
        """
        return 1 - player

    def switch_player(self):
        """
        Change the current player.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Perform the move (pile, count) for the current player.
        """
        pile, count = action

        if self.winner is not None:
            raise Exception("Game already ended")

        if pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile index")

        if count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects to remove")

        self.piles[pile] -= count
        self.switch_player()

        # Check if game ended
        if all(p == 0 for p in self.piles):
            # The player who just moved caused game over, so the other player wins
            self.winner = self.player


class NimAI:
    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize Q-learning AI.
        """
        self.q = {}  # key: (state, action), value: Q-value
        self.alpha = alpha
        self.epsilon = epsilon

    def get_q_value(self, state, action):
        """
        Return Q-value for (state, action), or 0 if unseen.
        """
        return self.q.get((tuple(state), action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update Q-value using learning formula.
        """
        new_estimate = reward + future_rewards
        self.q[(tuple(state), action)] = old_q + self.alpha * (new_estimate - old_q)

    def best_future_reward(self, state):
        """
        Return max Q-value for all possible actions in state.
        """
        actions = Nim.available_actions(state)
        if not actions:
            return 0

        max_q = max(self.get_q_value(state, action) for action in actions)
        return max_q

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-values based on transition and reward.
        """
        old_q = self.get_q_value(old_state, action)
        future_rewards = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old_q, reward, future_rewards)

    def choose_action(self, state, epsilon=True):
        """
        Choose an action using epsilon-greedy policy.
        """
        actions = list(Nim.available_actions(state))
        if not actions:
            return None

        # Random action with probability epsilon
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)

        # Choose action with highest Q-value
        max_q = float('-inf')
        best_actions = []
        for action in actions:
            q = self.get_q_value(state, action)
            if q > max_q:
                max_q = q
                best_actions = [action]
            elif q == max_q:
                best_actions.append(action)

        return random.choice(best_actions)


def train(n):
    """
    Train AI by playing against itself n times.
    """
    player = NimAI()

    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()
        last_moves = {0: {"state": None, "action": None},
                      1: {"state": None, "action": None}}

        while True:
            state = game.piles.copy()
            action = player.choose_action(state)

            last_moves[game.player]["state"] = state
            last_moves[game.player]["action"] = action

            game.move(action)
            new_state = game.piles.copy()

            if game.winner is not None:
                # Penalize the player who just moved
                player.update(state, action, new_state, -1)
                # Reward the other player (the winner)
                player.update(
                    last_moves[game.player]["state"],
                    last_moves[game.player]["action"],
                    new_state,
                    1
                )
                break
            else:
                if last_moves[game.player]["state"] is not None:
                    player.update(
                        last_moves[game.player]["state"],
                        last_moves[game.player]["action"],
                        new_state,
                        0
                    )

    print("Done training")
    return player


def play(ai, human_player=None):
    """
    Play against the trained AI.
    """
    if human_player is None:
        human_player = random.choice([0, 1])

    game = Nim()

    while True:
        print("\nPiles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        available = Nim.available_actions(game.piles)
        time.sleep(1)

        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose pile: "))
                count = int(input("Choose count: "))
                if (pile, count) in available:
                    break
                else:
                    print("Invalid move, try again.")
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        game.move((pile, count))

        if game.winner is not None:
            print("\nGAME OVER")
            winner = "You" if game.winner == human_player else "AI"
            print(f"{winner} won!")
            break


if __name__ == "__main__":
    trained_ai = train(10000)
    play(trained_ai)
