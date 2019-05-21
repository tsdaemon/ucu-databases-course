import glob
import json
from threading import Lock
from functools import reduce

from flask import Flask, jsonify, request, abort

app = Flask(__name__)


class SimpleBlock(object):
    def __init__(self, name, num):
        self.name = name
        self.num = num
        self.lock = Lock()

    def _get_filename(self):
        return "{}{}.json".format(self.name, self.num)

    def read(self):
        with self.lock:
            filename = self._get_filename()
            with open(filename, 'r') as f:
                return json.load(f)

    def write(self, records):
        with self.lock:
            filename = self._get_filename()
            with open(filename, 'w') as f:
                json.dump(records, f)


class SimpleFilesystemRepository(object):
    def __init__(self, tablename, number_of_elements_in_block=10):
        self.blocks = self._register_all_blocks(tablename)
        self.last_index = self._get_last_index()
        self.index_lock = Lock()

        self.tablename = tablename
        self.number_of_elements_in_block = number_of_elements_in_block

    def _register_all_blocks(self, tablename):
        all_file_names = glob.glob('{}*.json'.format(tablename))
        blocks = []
        for file_name in all_file_names:
            num = int(file_name[len(tablename):-5])
            block = SimpleBlock(tablename, num)
            blocks.append(block)

        return blocks

    def _get_last_index(self):
        if len(self.blocks) == 0:
            return 0

        last_block = self.blocks[-1]
        records = last_block.read()
        last_index = max((r['id'] for r in records),
                         default=self.number_of_elements_in_block*len(self.blocks))
        return last_index

    def _get_block_num_by_id(self, id):
        # import pdb; pdb.set_trace()
        return id // self.number_of_elements_in_block

    def get_all(self):
        return reduce(lambda x, y: x + y, (block.read() for block in self.blocks), [])

    def get_one(self, id):
        number_of_block = self._get_block_num_by_id(id)
        if number_of_block >= len(self.blocks):
            return None

        block = self.blocks[number_of_block]
        elements = block.read()
        for element in elements:
            if element['id'] == id:
                return element

        return None

    def create(self, record):
        with self.index_lock:
            self.last_index += 1

            record['id'] = self.last_index

            if self.last_index % self.number_of_elements_in_block == 1:
                new_block = SimpleBlock(self.tablename, self._get_block_num_by_id(self.last_index))
                records = [record]
                new_block.write(records)
                self.blocks.append(new_block)
            else:
                last_block = self.blocks[-1]
                with last_block.lock:
                    records = last_block.read()
                    records.append(record)
                    last_block.write(records)

        return record

    def update(self, record):
        id = record['id']
        number_of_block = self._get_block_num_by_id(id)
        if number_of_block >= len(self.blocks):
            return False

        update_block = self.blocks[number_of_block]

        with update_block.lock:
            records = update_block.read()
            old_record = next((r for r in records if r['id'] == id), None)
            if old_record is None:
                return False
            old_record.update(record)
            update_block.write(records)

        return True

    def delete(self, id):
        number_of_block = self._get_block_num_by_id(id)
        if number_of_block >= len(self.blocks):
            return False

        delete_block = self.blocks[number_of_block]

        with delete_block.lock:
            records = delete_block.read()
            index = next((i for i, r in enumerate(records) if r['id'] == id), None)
            if index is None:
                return False
            records.pop(index)
            delete_block.write(records)

        return True


repository = SimpleFilesystemRepository('cohorts')


@app.route('/cohorts')
def list_cohorts():
    cohorts = repository.get_all()
    return jsonify(cohorts)


@app.route('/cohorts/<int:id>')
def get_cohorts(id):
    cohort = repository.get_one(id)

    if cohort is None:
        abort(404)

    return jsonify(cohort)


@app.route('/cohorts', methods=['POST'])
def create_cohort():
    cohort = request.get_json()

    cohort = repository.create(cohort)

    return jsonify(cohort), 201


@app.route('/cohorts', methods=['PUT'])
def update_cohort():
    cohort = request.get_json()

    success = repository.update(cohort)
    if not success:
        abort(404)

    return jsonify(cohort)


@app.route('/cohorts/<int:id>', methods=['DELETE'])
def delete_cohort(id):
    success = repository.delete(id)

    if not success:
        abort(404)

    return "", 200


if __name__ == '__main__':
    app.run(debug=True)
