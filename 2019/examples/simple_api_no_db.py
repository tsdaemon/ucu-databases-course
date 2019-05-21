from flask import Flask, jsonify, request, abort, Response
import os
import json

app = Flask(__name__)

STORAGE_FILE_NAME = "cohorts.json"

if not os.path.isfile(STORAGE_FILE_NAME):
    with open(STORAGE_FILE_NAME, "w") as file:
        file.write("[]")


@app.route('/cohorts')
def list_cohorts():
    with open(STORAGE_FILE_NAME, "r") as file:
        cohorts = file.read()
    return cohorts


@app.route('/cohorts/<int:id>')
def get_cohorts(id):
    with open(STORAGE_FILE_NAME, "r") as file:
        cohorts = json.load(file)

    cohort = next((c for c in cohorts if c["id"] == id), None)
    if cohort is None:
        abort(404)

    return jsonify(cohort)


@app.route('/cohorts', methods=['POST'])
def create_cohort():
    cohort = request.get_json()

    with open(STORAGE_FILE_NAME, "r") as file:
        cohorts = json.load(file)

    last_id = max([e["id"] for e in cohorts], default=0)
    cohort["id"] = last_id + 1
    cohorts.append(cohort)

    with open(STORAGE_FILE_NAME, "w") as file:
        json.dump(cohorts, file)

    return jsonify(cohort), 201


@app.route('/cohorts', methods=['PUT'])
def update_cohort():
    cohort = request.get_json()
    id = cohort["id"]

    with open(STORAGE_FILE_NAME, "r") as file:
        cohorts = json.load(file)

    old_cohort = next((c for c in cohorts if c["id"] == id), None)
    if old_cohort is None:
        abort(404)

    old_cohort.update(cohort)

    with open(STORAGE_FILE_NAME, "w") as file:
        json.dump(cohorts, file)

    return jsonify(old_cohort)


@app.route('/cohorts/<int:id>', methods=['DELETE'])
def delete_cohort(id):
    with open(STORAGE_FILE_NAME, "r") as file:
        cohorts = json.load(file)

    new_cohorts = [*filter(lambda x: x["id"] != id, cohorts)]

    if len(new_cohorts) == len(cohorts):
        abort(404)

    with open(STORAGE_FILE_NAME, "w") as file:
        json.dump(new_cohorts, file)

    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
