import random as rnd
import requests
from time import time
import concurrent.futures
import string
import traceback

THREADS = 2
TOTAL_OPERATIONS = 1000
MAX_ID = 200


journal = []


def get_url(id=None):
    url = 'http://localhost:5000/cohorts/'
    if id is None:
        return url
    else:
        return url + str(id)


def random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(rnd.choice(letters) for _ in range(length))


def get_all():
    return requests.get(get_url()).json()


def get_single(id=None):
    if id is None:
        id = rnd.randint(1, MAX_ID)
    requests.get(get_url(id))


def create():
    entity = {'name': random_string()}
    result = requests.post(get_url(), json=entity).json()
    journal.append(('create', result))


def update(id=None):
    if id is None:
        id = rnd.randint(1, MAX_ID)
    entity = {'name': random_string(), 'id': id}

    r = requests.put(get_url(), json=entity)
    if r.status_code == 200:
        journal.append(('update', entity))


def delete(id=None):
    if id is None:
        id = rnd.randint(1, MAX_ID)

    r = requests.delete(get_url(id))
    if r.status_code == 200:
        journal.append(('delete', id))


operations = {
    0: get_all,
    1: get_single,
    2: create,
    3: update,
    4: delete
}


def worker_test_api(_):
    rnd_op_id = rnd.randint(0, 4)
    rnd_op = operations[rnd_op_id]
    try:
        rnd_op()
    except Exception:
        traceback.print_exc()
        pass


def assert_journal_is_correct(prev_records):
    remote_records = {e['id']: e for e in get_all()}

    # add journaled actions into current state making it expected state
    for action, value in journal:
        if action == 'create' or action == 'update':
            prev_records[value['id']] = value
        elif action == 'delete':
            del prev_records[value]

    assert remote_records == prev_records


def test_application_benchmark():
    # save current state
    prev_records = {e['id']: e for e in get_all()}

    # benchmark operations time
    start = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(worker_test_api, range(TOTAL_OPERATIONS))
    end = time()
    print('Spent time: {}'.format(end-start))

    # check that actual API changes equals to expected
    assert_journal_is_correct(prev_records)


if __name__ == '__main__':
    test_application_benchmark()
