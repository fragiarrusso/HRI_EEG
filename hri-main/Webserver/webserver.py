from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import random

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Memory.queries import *
from Knowledge.tris import *
from Utils.constants import *
from MentalModel.mentalTris import *

trisHandler = TrisInteractionHandler()

app = Flask(__name__)
CORS(app)

@app.route('/api/loginUser', methods=['POST'])
def loginUser():
    data = request.json  # Get JSON data sent to the server
    username = data['username']
    result = createUser(username)

    message = f"Welcome {username}"

    print(result)

    if result['new_account'] is False:
        message = f"Welcome back {username}"
    

    # trisHandler.newUser(message)
    
    return jsonify({'success': True, 'message': message})  # Return JSON response

@app.route('/api/makeMove', methods=['POST'])
def makeMove():
    data = request.json
    boardGame = data['boardGame']
    username = data['username']

    level = getLevel(username)
    aiMove = find_best_move(boardGame)

    print(level)
    level = level[0]['level']

    if level == 'BEGINNER':
        aiMove = choose_random_move(boardGame)
    elif level == 'INTERMEDIATE':
        if random.uniform(0, 1) < INTERMEDIATE_RANDOM:
            aiMove = choose_random_move(boardGame)
            print(f"random move: {aiMove}")
    

    
    return jsonify({'success': True, 'boardGame': boardGame, 'aiMove': aiMove})  # Return JSON response

@app.route('/api/setResultMatch', methods=['POST'])
def setResultMatch():
    data = request.json  # Get JSON data sent to the server
    username = data['username']
    winner = data['winner']

    result = setWinner(username, winner)

    trisHandler.endMatch(winner, username)

    return jsonify(result)  # Return JSON response

@app.route('/api/checkLevel', methods=['POST'])
def checkLevel():
    data = request.json  # Get JSON data sent to the server
    username = data['username']
    print(f"username: {username}")
    matches = getMatches(username)
    level = getLevel(username)[0]['level']

    result = {
        'success': True
    }
    print(matches)

    ratio = 0
    if len(matches) > 0:
        ai_wins = matches[0]['AI_wins']
        human_wins = matches[0]['human_wins']
        if ai_wins == None:
            ratio = 1
        elif ai_wins == 0:
            ratio = human_wins
        else:
            ratio = human_wins / ai_wins
    
    new_level = ''
    if ratio >=PRO_RATIO:
        new_level = 'PRO'
    elif ratio >= INTERMEDIATE_RATIO:
        new_level = 'INTERMEDIATE'
    else:
        new_level = 'BEGINNER'

    # #TODO logic to make the robot speak and tell the user he leveled up or down
    # level = level if level is not None else 'beginner'
    # if LEVELS[level] < LEVELS[new_level]:
    #     #leveled up
    #     print()
    # elif LEVELS[level] > LEVELS[new_level]:
    #     #leveled down
    #     print()
    # else:
    #     #not changed
    #     print()


    response = setLevel(username, new_level)
    result['level'] = new_level
    result['change'] = response

    
    trisHandler.levelChange(level, new_level)

    return jsonify(result)  # Return JSON response

@app.route('/api/getLevel', methods=['POST'])
def getLevelApi():
    data = request.json  # Get JSON data sent to the server
    username = data['username']
    result = getLevel(username)
    return jsonify(result[0]['level'])  # Return JSON response


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)  # Run the server


# @app.route('/api/loginUser', methods=['GET'])
# def get_data():
#     print("Entrato")
#     return "ciao"
#     # data = request.json  # Get JSON data sent to the server
#     # return jsonify(data)  # Return JSON response

# @app.route('/api/query')
# def get_query():
#     query = request.args.get('query')
#     return f"ciao {query}"

# @app.route('/api/data/<username>')
# def get_username(username):
#     print(f"Entrato {username}")
#     return f"ciao {username}"