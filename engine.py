import chess
import random

# Piece values
piece_score = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000}

# Piece-Square Tables (simplified)
# These tables are instrumental for positional evaluation.
# A more advanced engine would have different tables for opening, middlegame, and endgame.
pawn_eval_white = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [10,10, 20, 30, 30, 20, 10, 10],
    [50,50, 50, 50, 50, 50, 50, 50],
    [0,  0,  0,  0,  0,  0,  0,  0]
]
pawn_eval_black = pawn_eval_white[::-1]

# ... (similar tables for Knight, Bishop, Rook, Queen, King)
# For brevity, only pawn table is fully shown. Add other tables for stronger play.

piece_position_scores = {
    "P": pawn_eval_white,
    "p": pawn_eval_black,
    # Add other piece types here...
}


def evaluate_board(board):
    """
    Evaluates the board position. A positive score favors White, negative favors Black.
    *** THIS IS WHERE YOU WOULD INTEGRATE A CNN or NNUE MODEL ***
    Instead of hand-crafted tables, a neural network would take the board state
    as input and output a single evaluation score.
    """
    if board.is_checkmate():
        if board.turn: return -9999 # Black wins
        else: return 9999 # White wins
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.symbol().upper()
            piece_val = piece_score[piece_type]
            
            # Positional score from table
            pos_score = 0
            if piece.symbol() in piece_position_scores:
                row, col = divmod(square, 8)
                pos_score = piece_position_scores[piece.symbol()][row][col]
            
            if piece.color == chess.WHITE:
                score += piece_val + pos_score
            else:
                score -= (piece_val + pos_score)
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with Alpha-Beta pruning to find the best move.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    # Move ordering - captures first
    legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move(board, depth):
    """
    Finds the best legal move for the current player.
    """
    best_move = None
    max_eval = -float('inf')
    min_eval = float('inf')
    
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
        
    random.shuffle(legal_moves) # Add variety to openings

    for move in legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, -float('inf'), float('inf'), board.turn == chess.BLACK)
        board.pop()

        if board.turn == chess.WHITE: # Maximizing player
            if eval > max_eval:
                max_eval = eval
                best_move = move
        else: # Minimizing player
             if eval < min_eval:
                min_eval = eval
                best_move = move
                
    return best_move if best_move else legal_moves[0]