from pickle import load, dump


def pickle(obj, file):
    with open(file, 'wb') as f:
        dump(obj, f)


def unpickle(file):
    with open(file, 'rb') as pickle_file:
        return load(pickle_file)