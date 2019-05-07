from flask import Flask, jsonify, request, abort, Response
import mysql.connector

app = Flask(__name__)


def db():
    conn = mysql.connector.connect(host='localhost', user='root', password='1qaz2wsx', database='university2')
    return conn


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
