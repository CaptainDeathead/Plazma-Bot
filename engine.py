import chess
import random
import os
import boardmaps
import threading as th

# Initialize transposition table as a dictionary
transposition_table = {}

# Initialize Zobrist hash table for piece-square positions
zobrist_table = {}
for square in chess.SQUARES:
    for piece in chess.PIECE_TYPES:
        for color in chess.COLORS:
            zobrist_table[(piece, square, color)] = random.getrandbits(64)

# Calculate Zobrist hash for the current position
def calculate_zobrist_hash(board):
    hash_value = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_type = piece.piece_type
            color = piece.color
            hash_value ^= zobrist_table[(piece_type, square, color)]

    return hash_value

def evaluate_board(board):
    # Simple evaluation function that counts the material value of the pieces
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0  # Not used in evaluation
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
                score += boardmaps.value(piece.piece_type, square)
            else:
                score -= value

    score += EndGame(board)

    return score

def get_ordered_moves(board):
    moves = []
    bad_moves = []

    for move in board.legal_moves:
        # Make the move
        board.push(move)

        # Check if the king is in check after the move
        if not board.is_check():
            # Add capturing moves to the list
            if board.is_capture(move):
                moves.append(move)
            # Add non-capturing moves to the list
            else:
                bad_moves.append(move)

        # Undo the move
        board.pop()

    moves += bad_moves

    return moves

def minimax(board, depth, alpha, beta, maximizing_player):
    # Calculate Zobrist hash for the current position
    hash_value = calculate_zobrist_hash(board)

    # Store evaluation in transposition table
    #if len(transposition_table) > 50000:
    #    # remove the oldest entry
    #    transposition_table.popitem()

    # Check transposition table for stored evaluation
    #if hash_value in transposition_table:
    #    entry = transposition_table[hash_value]
    #    if entry['depth'] >= depth:
    #        if entry['flag'] == 'EXACT':
    #            return entry['eval']
    #        elif entry['flag'] == 'LOWERBOUND':
    #            alpha = max(alpha, entry['eval'])
    #        elif entry['flag'] == 'UPPERBOUND':
    #            beta = min(beta, entry['eval'])
#
    #        if alpha >= beta:
    #            return entry['eval']

    if depth == 0 or board.is_game_over():
        evaluation = evaluate_board(board)

        # Store evaluation in transposition table
        transposition_table[hash_value] = {'eval': evaluation, 'depth': depth, 'flag': 'EXACT'}

        return evaluation

    if maximizing_player:
        max_eval = float("-inf")
        ordered_moves = get_ordered_moves(board)
        for move in ordered_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        # Store evaluation in transposition table
        transposition_table[hash_value] = {'eval': max_eval, 'depth': depth, 'flag': 'LOWERBOUND'}

        return max_eval
    else:
        min_eval = float("inf")
        ordered_moves = get_ordered_moves(board)
        for move in ordered_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
    
        transposition_table[hash_value] = {'eval': min_eval, 'depth': depth, 'flag': 'UPPERBOUND'}

        return min_eval

def get_best_move(board, depth):
    best_move = None
    max_eval = float("-inf")

    ordered_moves = get_ordered_moves(board)
    for move in ordered_moves:
        board.push(move)
        eval = minimax(board, depth - 1, float("-inf"), float("inf"), False)
        board.pop()

        if eval > max_eval:
            max_eval = eval
            best_move = move

    return best_move

def EndGame(board):
    evaluation = 0

    # Favors positions where the player's pieces can deliver checkmate
    # when there are only a few pieces left on the board
    if board.is_checkmate() and board.turn == chess.WHITE:
        evaluation -= 10000

    elif board.is_checkmate() and board.turn == chess.BLACK:
        evaluation += 10000

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
        # Lower evaluation for stalemate or insufficient material
        evaluation -= 10000

    return evaluation

def process(board, color, moves_played, depth = 4):
    if moves_played < 2:
        best_move = random.choice(list(board.legal_moves))

    else:
        best_move = get_best_move(board, depth)

    return best_move, moves_played + 1

if __name__ == "__main__":
    os.system("python3 main.py")