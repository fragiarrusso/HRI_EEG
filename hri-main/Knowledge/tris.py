import random

board = [None] * 9
# board[0] = 'X'
# board[1] = 'X'
# board[2] = 'O'
# board[3] = 'O'
# board[4] = 'O'
# board[5] = 'X'
# board[6] = 'X'
# board[7] = 'O'
# board[8] = 'X'


AI = 'X'    # AI's marker
HUMAN = 'O' # Human's marker
scores = {AI: 1, HUMAN: -1, None: 0}  # Score values for minimax algorithm
winningCombinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], 
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6]            
    ]

def check_winner(board):
    winner = None 
    for i in range(len(winningCombinations)):
        [a, b, c] = winningCombinations[i]
        if board[a] is not None and board[a] == board[b] and board[a] == board[c]:
            winner = board[a]
            break
    return winner

def make_move(board, move, actor):
    board[move] = actor
    return

def undo_move(board, move):
    board[move] = None
    return

def get_available_moves(board):
    return [index for index in range(len(board)) if board[index] is None]

def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    # print(f'board: {board}, depth: {depth}, is_maximizing: {is_maximizing} winner: {winner}')
    if winner is not None or depth == 0:
        return scores[winner]

    if is_maximizing:
        best_score = float('-inf')
        for move in get_available_moves(board):
            make_move(board, move, AI)
            score = minimax(board, depth - 1, False)
            undo_move(board, move)
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in get_available_moves(board):
            make_move(board, move, HUMAN)
            score = minimax(board, depth - 1, True)
            undo_move(board, move)
            best_score = min(score, best_score)
        return best_score

def check_first_move(board):
    counter = 0
    for elem in board:
        if elem is None:
            counter += 1
    if counter == 9:
        return True
    
    return False

def find_best_move(board):
    if check_first_move(board) is True:
        return random.randint(0, 8)
    
    best_score = float('-inf')
    best_move = None
    for move in get_available_moves(board):
        make_move(board, move, AI)
        score = minimax(board, len(get_available_moves(board)), False)
        undo_move(board, move)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move

def choose_random_move(board):
    available_moves = get_available_moves(board)
    available_moves = available_moves if len(available_moves) >= 0 else 0
    ranodm_move = random.randint(0, len(available_moves) - 1) 
    return available_moves[ranodm_move]

if __name__ == "__main__":
    # print(check_winner(board))
    # print(f'available: {get_available_moves(board)}')
    print(find_best_move(board))
