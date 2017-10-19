from translator.relation import Relation


class Node(object):

    DB = None

    @classmethod
    def get_class_rs_relations(cls):
        if not hasattr(cls, '_RS_RELATIONS'):
            cls._RS_RELATIONS = []
        return cls._RS_RELATIONS

    def __init__(self, dn):
        assert self.DB
        assert dn
        self.dn = dn
        self.mo = dn
        self.updates = []
        self.rt_relations = []
        self.rs_relations = None
        self.DB.add(self)
        self.update_relations(self, 'create')

    def get_rs_relations(self):
        return Node.get_class_rs_relations()

    def append_relations(self, endp_dn, origp):
        result, error = origp.validate_append_relation(endp_dn)
        assert result, error
        self.get_rs_relations().append([endp_dn, origp])
        print('append relation {0} to {1}'.format(origp.dn, endp_dn))

    def remove_relations(self, endp_dn, origp):
        result, error = origp.validate_remove_relation(endp_dn)
        assert result, error
        self.get_rs_relations().remove([endp_dn, origp])
        print('remove relation {0} to {1}'.format(origp.dn, endp_dn))

    def update_relations(self, endp, reason):
        for trav_endp_dn, trav_orig in self.get_rs_relations()[:]:
            if trav_endp_dn == endp.dn:
                result, error = trav_orig.validate_relation(endp)
                assert result, error
                result, error = endp.validate_relation(trav_orig)
                assert result, error
                self.remove_relations(endp.dn, trav_orig)
                trav_orig.update_rs_relation(endp, reason)
                endp.add_rt_relation(trav_orig.dn)

    def validate_append_relation(self, endp_dn):
        return True, None

    def validate_remove_relation(self, endp_dn):
        return True, None

    def validate_relation(self, endp):
        return True, None

    def add_rs_relation(self, dn):
        endp = self.DB.find(dn)
        if endp is None:
            self.rs_relations = Relation(dn, "RS", False)
            self.append_relations(dn, self)
            print('RS {} not found'.format(dn))
        else:
            assert self.validate_relation(endp)
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
            origp = self.DB.find(entry.dn)
            origp.update_rs_relation(self, reason)

        if self.rs_relations:
            endp = self.DB.find(self.rs_relations.dn)
            if endp:
                for entry in [x for x in endp.rt_relations[:] if x.dn == self.dn]:
                    entry.update(reason)

    def delete(self):
        if self.rs_relations and self.rs_relations.dn:
            endp = self.DB.find(self.rs_relations.dn)
            if endp is not None:
                endp.update_rt_relation(self, 'delete')
            else:
                self.remove_relations(self.rs_relations.dn, self)

        for entry in self.rt_relations:
            origp = self.DB.find(entry.dn)
            origp.update_rs_relation(self, 'delete')
            self.append_relations(self.dn, origp)

        self.DB.delete(self.dn)
