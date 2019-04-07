from flask import Blueprint, abort

students = Blueprint('students', __name__)


@students.route('/')
def list_students():
    abort(501)  # not implemented


@students.route('/<int:id>')
def get_student(id):
    abort(501)  # not implemented


@students.route('/', methods=['POST'])
def create_student():
    abort(501)  # not implemented


@students.route('/', methods=['PUT'])
def update_student():
    abort(501)  # not implemented


@students.route('/<int:id>', methods=['DELETE'])
def delete_student(id):
    abort(501)  # not implemented
