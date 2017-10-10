from db import get_db
from relation import Relation


class Node(object):

    __RS_RELATIONS = []

    @classmethod
    def append_relations(cls, endp_dn, origp):
        cls.__RS_RELATIONS.append([endp_dn, origp])
        print('append relation {0} to {1}'.format(origp.dn, endp_dn))

    @classmethod
    def remove_relations(cls, endp_dn, origp):
        cls.__RS_RELATIONS.remove([endp_dn, origp])
        print('remove relation {0} to {1}'.format(origp.dn, endp_dn))

    @classmethod
    def update_relations(cls, endp, reason):
        for trav_endp_dn, trav_orig in cls.__RS_RELATIONS[:]:
            if trav_endp_dn == endp.dn:
                cls.remove_relations(endp.dn, trav_orig)
                trav_orig.update_rs_relation(endp, reason)
                endp.add_rt_relation(trav_orig.dn)

    @classmethod
    def get_rs_relations(cls):
        return cls.__RS_RELATIONS

    def __init__(self, dn):
        self.dn = dn
        self.mo = dn
        self.updates = []
        self.rt_relations = []
        self.rs_relations = None
        get_db().add(self)
        self.update_relations(self, 'create')

    def add_rs_relation(self, dn):
        endp = get_db().find(dn)
        if endp is None:
            self.rs_relations = Relation(dn, "RS", False)
            self.append_relations(dn, self)
            print('RS {} not found'.format(dn))
        else:
            self.rs_relations = Relation(dn, "RS", True)
            endp.add_rt_relation(self.dn)
            print('RS {} found'.format(dn))

    def add_rt_relation(self, dn):
        self.rt_relations.append(Relation(dn, "RT", True))
        print('RT {} appended'.format(dn))

    def update_rs_relation(self, endp, reason):
        print('{0} update rs-relation {1}'.format(endp.dn, reason))
        assert self.rs_relations.dn == endp.dn
        # Here should be the specific code to apply when the relation
        # is satisfacied.
        self.rs_relations.update(reason)

    def update_rt_relation(self, origp, reason):
        print('{0} update rt-relation {1}'.format(origp.dn, reason))
        for entry in [x for x in self.rt_relations[:] if x.dn == origp.dn]:
            if reason == 'delete':
                self.rt_relations.remove(entry)
                break

    def update(self, reason):
        self.updates.append(reason)
        for entry in self.rt_relations:
            origp = get_db().find(entry.dn)
            origp.update_rs_relation(self, reason)

        if self.rs_relations:
            endp = get_db().find(self.rs_relations.dn)
            if endp:
                for entry in [x for x in endp.rt_relations[:] if x.dn == self.dn]:
                    entry.update(reason)

    def delete(self):
        if self.rs_relations and self.rs_relations.dn:
            endp = get_db().find(self.rs_relations.dn)
            if endp is not None:
                endp.update_rt_relation(self, 'delete')
            else:
                self.remove_relations(self.rs_relations.dn, self)

        for entry in self.rt_relations:
            origp = get_db().find(entry.dn)
            origp.update_rs_relation(self, 'delete')
            self.append_relations(self.dn, origp)

        get_db().delete(self.dn)
