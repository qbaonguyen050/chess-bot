import chess
import random

# Piece values
piece_score = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000}

# Piece-Square Tables (simplified for speed and clarity)
# For a 2800+ Elo engine, these would be replaced by a trained neural network (CNN/NNUE)
pawn_eval = [
    [0,0,0,0,0,0,0,0],[5,10,10,-20,-20,10,10,5],[5,-5,-10,0,0,-10,-5,5],
    [0,0,0,20,20,0,0,0],[5,5,10,25,25,10,5,5],[10,10,20,30,30,20,10,10],
    [50,50,50,50,50,50,50,50],[0,0,0,0,0,0,0,0]
]
knight_eval = [
    [-50,-40,-30,-30,-30,-30,-40,-50],[-40,-20,0,5,5,0,-20,-40],
    [-30,5,10,15,15,10,5,-30],[-30,0,15,20,20,15,0,-30],
    [-30,5,15,20,20,15,5,-30],[-30,0,10,15,15,10,0,-30],
    [-40,-20,0,0,0,0,-20,-40],[-50,-40,-30,-30,-30,-30,-40,-50]
]
# Add tables for Bishop, Rook, etc. for a stronger engine

piece_position_scores = { "P": pawn_eval, "N": knight_eval }

def evaluate_board(board):
    if board.is_checkmate(): return -9999 if board.turn else 9999
    if board.is_stalemate(): return 0

    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = piece_score[piece.symbol().upper()]
            pos_score = 0 # Placeholder for positional evaluation
            if piece.symbol().upper() in piece_position_scores:
                 # A real implementation needs to correctly orient the board
                 pass # Simplified for now
            if piece.color == chess.WHITE: score += val + pos_score
            else: score -= val + pos_score
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    moves = sorted(list(board.legal_moves), key=lambda m: board.is_capture(m), reverse=True)
    
    if maximizing_player:
        max_eval = -float('inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

def get_best_move(board, depth):
    best_move = None
    max_eval, min_eval = -float('inf'), float('inf')
    is_maximizing = board.turn == chess.WHITE
    
    # Use a shuffled list to ensure variety in openings if scores are equal
    moves = list(board.legal_moves)
    random.shuffle(moves)

    for move in moves:
        board.push(move)
        eval = minimax(board, depth - 1, -float('inf'), float('inf'), not is_maximizing)
        board.pop()
        if is_maximizing and eval > max_eval:
            max_eval, best_move = eval, move
        elif not is_maximizing and eval < min_eval:
            min_eval, best_move = eval, move
            
    # Fallback to a random move if no best move is found (should not happen in normal play)
    return best_move or (moves[0] if moves else None)