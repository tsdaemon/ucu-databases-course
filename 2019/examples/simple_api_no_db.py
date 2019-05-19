from flask import Flask, jsonify, request, abort, Response
import os
import json
import threading

app = Flask(__name__)

STORAGE_FILE_PREFIX = "cohorts"
STORAGE_FILE_SUFFIX = ".json"
INDEX_FILE_NAME = "cohorts-index.json"

FILE_RECORDS = 10

mutex_index = threading.Lock()
mutex_dict = {}

if not os.path.isfile(INDEX_FILE_NAME):
    index = {"files_number": 0}

    with open(INDEX_FILE_NAME, "w") as file:
        json.dump(index, file)
else:
    with open(INDEX_FILE_NAME, "r") as file:
        index = json.load(file)

    for i in range(index["files_number"]):
        mutex_dict[i] = threading.Lock()

def get_fn(num):
    return STORAGE_FILE_PREFIX + str(num) + STORAGE_FILE_SUFFIX

def get_num_from_id(id):
    return int(id / FILE_RECORDS)

def read_index():
    with mutex_index:
        with open(INDEX_FILE_NAME, "r") as file:
            index = json.load(file)
    return  index

@app.route('/cohorts')
def list_cohorts():
    index = read_index()

    cohorts = []
    for file_num in range(index["files_number"]):
        with mutex_dict[file_num]:
            with open(get_fn(file_num) , "r") as file:
                cohorts_i = json.load(file)
                cohorts.extend(cohorts_i)
    return jsonify(cohorts)


@app.route('/cohorts/<int:id>')
def get_cohorts(id):
    if get_num_from_id(id) not in mutex_dict:
        abort(404)

    with mutex_dict[get_num_from_id(id)]:
        with open(get_fn(get_num_from_id(id)), "r") as file:
            cohorts = json.load(file)

        cohort = next((c for c in cohorts if c["id"] == id), None)
        if cohort is None:
            abort(404)

    return jsonify(cohort)


@app.route('/cohorts', methods=['POST'])
def create_cohort():
    cohort = request.get_json()


    with mutex_index:
        with open(INDEX_FILE_NAME, "r") as file:
            index = json.load(file)

        if index["files_number"] == 0:
            mutex_dict[0] = threading.Lock()
            index["files_number"] = 1
            with open(INDEX_FILE_NAME, "w") as file:
                json.dump(index, file)

            cohort["id"] = 0
            with mutex_dict[0]:
                cohorts = [cohort]
                with open(get_fn(0), "w") as file:
                    json.dump(cohorts, file)
        else:
            with mutex_dict[index["files_number"] - 1]:
                with open(get_fn(index["files_number"] - 1), "r") as file:
                    cohorts = json.load(file)

                last_id = max([e["id"] for e in cohorts], default=0)
                cohort["id"] = last_id + 1
                if get_num_from_id(cohort["id"]) == get_num_from_id(last_id):
                    cohorts.append(cohort)

                    with open(get_fn(get_num_from_id(cohort["id"])), "w") as file:
                        json.dump(cohorts, file)
                else:
                    mutex_dict[index["files_number"]] = threading.Lock()
                    index["files_number"] += 1
                    with open(INDEX_FILE_NAME, "w") as file:
                        json.dump(index, file)
                    with mutex_dict[get_num_from_id(cohort["id"])]:
                        cohorts = [cohort]
                        with open(get_fn(get_num_from_id(cohort["id"])), "w") as file:
                            json.dump(cohorts, file)

    return jsonify(cohort), 201


@app.route('/cohorts', methods=['PUT'])
def update_cohort():
    cohort = request.get_json()
    id = cohort["id"]

    if get_num_from_id(id) not in mutex_dict:
        abort(404)

    with mutex_dict[get_num_from_id(id)]:
        with open(get_fn(get_num_from_id(id)), "r") as file:
            cohorts = json.load(file)

        old_cohort = next((c for c in cohorts if c["id"] == id), None)
        if old_cohort is None:
            abort(404)

        old_cohort.update(cohort)

        with open(get_fn(get_num_from_id(id)), "w") as file:
            json.dump(cohorts, file)

    return jsonify(old_cohort)


@app.route('/cohorts/<int:id>', methods=['DELETE'])
def delete_cohort(id):
    if get_num_from_id(id) not in mutex_dict:
        abort(404)

    with mutex_dict[get_num_from_id(id)]:

        with open(get_fn(get_num_from_id(id)), "r") as file:
            cohorts = json.load(file)

        new_cohorts = [*filter(lambda x: x["id"] != id, cohorts)]

        if len(new_cohorts) == len(cohorts):
            abort(404)

        if len(new_cohorts) == 0:
            with mutex_index:
                del mutex_dict[get_num_from_id(id)]

        with open(get_fn(get_num_from_id(id)), "w") as file:
            json.dump(new_cohorts, file)

    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
