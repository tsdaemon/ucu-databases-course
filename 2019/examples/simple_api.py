from flask import Flask, jsonify, request, abort

app = Flask(__name__)

students = []


@app.route('/students')
def list_students():
    return jsonify(students)


@app.route('/students/:id')
def get_student():
    id = request.args.get('id')
    abort(501)


@app.route('/students', methods=['POST'])
def create_student():
    abort(501)


@app.route('/students/:id', methods=['PUT'])
def update_student():
    id = request.args.get('id')
    abort(501)


@app.route('/students/:id', methods=['DELETE'])
def delete_student():
    id = request.args.get('id')
    abort(501)


if __name__ == '__main__':
    app.run(debug=True)
