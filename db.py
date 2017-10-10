class DB(object):

    def __init__(self):
        self.dbase = {}

    def add(self, entry):
        self.dbase[entry.dn] = entry
        print('Add {0}.{1}'.format(entry.dn, entry.__class__.__name__))

    def find(self, dn):
        try:
            return self.dbase[dn]
        except KeyError:
            return None

    def delete(self, dn):
        print('Delete {0}'.format(dn))
        del self.dbase[dn]


db = DB()


def get_db():
    return db
