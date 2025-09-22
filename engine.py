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
            if piece.color == chess.WHITE: score += val
            else: score -= val
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
    
    for move in board.legal_moves:
        board.push(move)
        eval = minimax(board, depth - 1, -float('inf'), float('inf'), not is_maximizing)
        board.pop()
        if is_maximizing and eval > max_eval:
            max_eval, best_move = eval, move
        elif not is_maximizing and eval < min_eval:
            min_eval, best_move = eval, move
            
    return best_move or random.choice(list(board.legal_moves))```

---

### **5. User Interface: `templates/index.html`**

A simple, fast-loading HTML file with a black background and a chat-like input for moves.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Codespace Chess Engine</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: monospace;
               display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        #board-container { width: 40vw; max-width: 400px; margin-bottom: 20px; }
        #controls input, #game-setup button { background-color: #333; color: #e0e0e0; border: 1px solid #555; padding: 10px; font-size: 1em; }
        #message { margin-top: 15px; height: 20px; color: #4caf50; }
    </style>
</head>
<body>
    <h1>Custom Chess Bot</h1>
    <div id="board-container"></div>
    <div id="game-setup">
        <p>Choose Your Side:</p>
        <button onclick="startGame('W')">Play as White</button>
        <button onclick="startGame('B')">Play as Black</button>
    </div>
    <div id="controls" style="display:none;">
        <input type="text" id="move-input" placeholder="Your move (e.g. e4, Nf3)" autocomplete="off">
        <button onclick="sendMove()">Submit</button>
        <p id="message"></p>
    </div>

    <script>
        const boardContainer = document.getElementById('board-container');
        const messageEl = document.getElementById('message');
        const moveInput = document.getElementById('move-input');

        function updateBoard() {
            fetch('/board_svg?t=' + new Date().getTime()) // Timestamp prevents caching
                .then(response => response.text())
                .then(svg => { boardContainer.innerHTML = svg; });
        }

        function startGame(color) {
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('controls').style.display = 'block';
            messageEl.textContent = `New game started. You play as ${color === 'W' ? 'White' : 'Black'}.`;
            fetch('/new_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({color: color})
            }).then(updateBoard);
        }

        function sendMove() {
            const move = moveInput.value;
            if (!move) return;
            messageEl.textContent = 'Engine is thinking...';
            fetch('/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({move: move})
            })
            .then(response => response.json())
            .then(data => {
                messageEl.textContent = data.error || data.message || '';
                if (data.game_over) {
                    document.getElementById('controls').style.display = 'none';
                }
                updateBoard();
            });
            moveInput.value = '';
        }

        moveInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') sendMove();
        });
    </script>
</body>
</html>