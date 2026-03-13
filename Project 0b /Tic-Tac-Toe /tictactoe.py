"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_count = sum(row.count(X) for row in board)
    O_count = sum(row.count(O) for row in board)
    return O if X_count > O_count else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if i not in [0, 1, 2] or j not in [0, 1, 2] or board[i][j] is not EMPTY:
        raise Exception("Invalid action")
    board_copy = deepcopy(board)
    board_copy[i][j] = player(board)
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]

    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or all(EMPTY not in row for row in board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    def max_value(board, alpha=-math.inf, beta=math.inf):
        if terminal(board):
            return utility(board), None
        v = -math.inf
        best_action = None
        for action in sorted(actions(board)):
            min_v, _ = min_value(result(board, action), alpha, beta)
            if min_v > v:
                v = min_v
                best_action = action
            alpha = max(alpha, v)
            if alpha >= beta:
                break
        return v, best_action

    def min_value(board, alpha=-math.inf, beta=math.inf):
        if terminal(board):
            return utility(board), None
        v = math.inf
        best_action = None
        for action in sorted(actions(board)):
            max_v, _ = max_value(result(board, action), alpha, beta)
            if max_v < v:
                v = max_v
                best_action = action
            beta = min(beta, v)
            if beta <= alpha:
                break
        return v, best_action

    if terminal(board):
        return None

    current_player = player(board)
    if current_player == X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]
