class Relation(object):

    def __init__(self, dn, rs_or_rt, state):
        self.dn = dn
        self.rs_or_rt = rs_or_rt
        self.state = state
        self.updates = []

    def update(self, reason):
        if reason == 'create':
            self.state = True
        elif reason == 'delete':
            self.state = False
        self.updates.append(reason)
