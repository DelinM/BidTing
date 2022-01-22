import os


def get_currentpath():
    return os.getcwd()


def get_Windows():
    op_system = os.name
    if op_system == 'posix':
        return False
    else:
        return True
