from flask import jsonify

from nlu_server import app


@app.route('/app', methods=['POST'])
def application():
    return jsonify({'hey': 'hello'})

