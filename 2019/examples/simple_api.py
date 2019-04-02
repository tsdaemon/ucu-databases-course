from flask import Flask, jsonify, request, abort, Response

app = Flask(__name__)

students = [
    {'id': 1, 'name': 'Ivan Petrov'}
]


@app.route('/students')
def list_students():
    return jsonify(students)


@app.route('/students/<int:id>')
def get_student(id):
    student = next((s for s in students if s['id'] == id), None)
    if student is None:
        abort(404)
    return jsonify(student)


@app.route('/students', methods=['POST'])
def create_student():
    student = request.get_json()

    max_id = max([s['id'] for s in students]) or 0
    student['id'] = max_id + 1
    students.append(student)

    return jsonify(student), 201


@app.route('/students', methods=['PUT'])
def update_student():
    student_new = request.get_json()
    # import pdb; pdb.set_trace()

    student = next((s for s in students if s['id'] == student_new['id']), None)
    if student is None:
        abort(404)

    student.update(student_new)
    return jsonify(student), 200


@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = next((s for s in students if s['id'] == id), None)
    if student is None:
        abort(404)

    students.remove(student)
    return Response('', status=201, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
