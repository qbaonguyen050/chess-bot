from flask import Flask, request, jsonify, render_template
import chess
import chess.svg
import engine

app = Flask(__name__)
board = None
ai_player = None

@app.route('/')
def index():
    """ Renders the main HTML page. """
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    """ Starts a new game, allowing the user to choose their color. """
    global board, ai_player
    board = chess.Board()
    color = request.json.get('color', 'W').upper()
    
    ai_player = chess.BLACK if color == 'W' else chess.WHITE

    # If AI is white, it makes the first move.
    if ai_player == chess.WHITE and not board.is_game_over():
        best_move = engine.get_best_move(board, 3) # Depth 3 for speed
        if best_move:
            board.push(best_move)

    return jsonify({'status': 'new game started', 'fen': board.fen()})

@app.route('/move', methods=['POST'])
def make_move():
    """ Handles the user's move and gets the engine's counter-move. """
    global board
    if board is None or board.is_game_over():
        return jsonify({'error': 'Game is not active'}), 400

    user_move_str = request.json.get('move')
    try:
        # Try SAN format first (e.g., Nf3)
        move = board.parse_san(user_move_str)
        board.push(move)
    except ValueError:
        try:
            # Fallback to UCI format (e.g., g1f3)
            move = chess.Move.from_uci(user_move_str)
            if move in board.legal_moves:
                board.push(move)
            else:
                raise ValueError
        except ValueError:
            return jsonify({'error': f"'{user_move_str}' is not a valid or legal move."}), 400

    if board.is_game_over():
        return jsonify({'status': 'game over', 'fen': board.fen(), 'message': 'Game is over!'})

    # AI's turn
    best_move = engine.get_best_move(board, 3) # Depth 3 for speed
    if best_move:
        board.push(best_move)

    return jsonify({
        'status': 'move processed',
        'fen': board.fen(),
        'game_over': board.is_game_over(),
        'message': f"AI played {best_move.uci()}" if best_move else "Your move."
    })

@app.route('/board_svg')
def board_svg():
    """ Generates an SVG image of the current board state for the UI. """
    if board is None:
        return chess.svg.board(), 200, {'Content-Type': 'image/svg+xml'}
    
    # Flip the board if the player chose black
    flipped = (ai_player == chess.WHITE)
    svg = chess.svg.board(board=board, flipped=flipped)
    return svg, 200, {'Content-Type': 'image/svg+xml'}

if __name__ == '__main__':
    # Host '0.0.0.0' makes it accessible within the Codespace environment
    app.run(host='0.0.0.0', port=5000)