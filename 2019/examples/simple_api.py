import os

from flask import Flask, jsonify, request, abort, Response
import mysql.connector

app = Flask(__name__)

students = [
    {'id': 1, 'name': 'Ivan Petrov'}
]


def db():
    conn = mysql.connector.connect(host='localhost', user='root', password='1qaz2wsx', database='university2')
    return conn


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


@app.route('/cohorts')
def list_cohorts():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cohorts")
    cohorts = cursor.fetchall()
    result = [dict(zip(cursor.column_names, c)) for c in cohorts]
    conn.close()
    return jsonify(result)


@app.route('/cohorts/<int:id>')
def get_cohorts(id):
    try:
        conn = db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cohorts WHERE id = %s", params=(id,))
        cohort = cursor.fetchone()
    except mysql.connector.Error as error:
        print(error)
        raise
    finally:
        conn.close()
        cursor.close()

    if cohort is None:
        abort(404)
    result = dict(zip(cursor.column_names, cohort))
    return jsonify(result)


@app.route('/cohorts', methods=['POST'])
def create_cohort():

    cohort = request.get_json()
    if cohort.keys() != {"name"}:
        abort(422)

    try:
        conn = db()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO cohorts (name) VALUES (%s)", (cohort["name"],))
        cohort["id"] = cursor.lastrowid

        conn.commit()
    except mysql.connector.Error as error:
        print(error)
        raise
    finally:
        conn.close()
        cursor.close()

    return jsonify(cohort), 201


@app.route('/cohorts', methods=['PUT'])
def update_cohort():

    cohort = request.get_json()
    if cohort.keys() != {"id", "name"}:
        abort(422)

    try:
        conn = db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cohorts WHERE id = %s", (cohort['id'],))
        existing_cohort = cursor.fetchone()
        if existing_cohort is None:
            abort(404)

        cursor.execute("UPDATE cohorts SET name=%(name)s WHERE id=%(id)s", cohort)
        conn.commit()
    except mysql.connector.Error as error:
        print(error)
        raise
    finally:
        conn.close()
        cursor.close()

    return jsonify(cohort)


@app.route('/cohorts/<int:id>', methods=['DELETE'])
def delete_cohort(id):
    try:
        conn = db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cohorts WHERE id = %s", (id,))
        existing_cohort = cursor.fetchone()
        if existing_cohort is None:
            abort(404)

        cursor.execute("DELETE FROM cohorts WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.Error as error:
        print(error)
        raise
    finally:
        conn.close()
        cursor.close()

    return jsonify({}), 200


if __name__ == '__main__':
    app.run(debug=True)
