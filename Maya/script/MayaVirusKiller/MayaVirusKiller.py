import os


def killing_virus(fpath):
    word = 'createNode script -n'
    del_list = []
    with open(fpath, 'r') as fp:
        lines = fp.readlines()
        found = 0
        for idx, line in enumerate(lines):
            if line.startswith(word) and '_gene' in line:
                found = 1
                del_list.append(idx)
                continue
            if found > 0 and line.startswith('	'):
                del_list.append(idx)
            if found > 0 and not line.startswith('	'):
                found -= 1
    for i in del_list:
        lines[i] = ''
    with open(fpath, 'w') as fp:
        fp.writelines(lines)


def fix_ma_with_subfolder(path):
    for r, d, f in os.walk(path):
        for i in f:
            if i[-3:] == '.ma':
                fpath = os.path.join(r, i)
                killing_virus(fpath)


def fix_ma(path):
    for i in os.listdir(path):
        if i[-3:] == '.ma':
            fpath = os.path.join(path, i)
            killing_virus(fpath)


path = r'I:\MXA\test'
fix_ma(path)
fix_ma_with_subfolder(path)
