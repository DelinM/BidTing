import os

def get_opsystem():
    op_system = os.name
    if op_system =='posix':
        return 'Unix'
    else:
        return 'Windows'

print(get_opsystem())