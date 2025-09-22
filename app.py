from flask import Flask, request, jsonify, render_template
import chess
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
    color = request.json.get('color')
    if color.upper() == 'W':
        ai_player = chess.BLACK
    elif color.upper() == 'B':
        ai_player = chess.WHITE
    else:
        return jsonify({'error': 'Invalid color choice. Use W or B.'}), 400

    # If AI is white, make the first move
    if ai_player == chess.WHITE and not board.is_game_over():
        best_move = engine.get_best_move(board, 3) # Depth 3 for speed
        if best_move:
            board.push(best_move)

    return jsonify({'status': 'new game started', 'fen': board.fen()})

@app.route('/move', methods=['POST'])
def make_move():
    """ Handles the user's move and gets the engine's counter-move. """
    global board, ai_player
    if board is None:
        return jsonify({'error': 'Game not started'}), 400

    if board.is_game_over():
        return jsonify({'status': 'game over', 'fen': board.fen(), 'message': 'Game is over.'})

    # User's turn
    user_move_san = request.json.get('move')
    try:
        move = board.parse_san(user_move_san)
        board.push(move)
    except ValueError:
        try:
            # Also try UCI format (e.g., e2e4)
            move = chess.Move.from_uci(user_move_san)
            if move in board.legal_moves:
                board.push(move)
            else:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid move format or illegal move'}), 400

    if board.is_game_over():
         return jsonify({'status': 'game over', 'fen': board.fen(), 'message': 'Congratulations, you won!'})

    # AI's turn
    best_move = engine.get_best_move(board, 3) # Depth 3 for speed
    if best_move:
        board.push(best_move)

    if board.is_game_over():
        return jsonify({'status': 'game over', 'fen': board.fen(), 'message': 'Game over. The AI wins.'})

    return jsonify({'fen': board.fen()})


@app.route('/board_svg', methods=['GET'])
def board_svg():
    """ Generates an SVG image of the current board state. """
    if board is None:
        return "No game in progress.", 404
    # Flip board if player is black
    flipped = (ai_player == chess.WHITE)
    svg = chess.svg.board(board=board, flipped=flipped)
    return svg, 200, {'Content-Type': 'image/svg+xml'}


if __name__ == '__main__':
    # Runs on all available interfaces in a Codespace, making it public.
    app.run(host='0.0.0.0', port=5000)