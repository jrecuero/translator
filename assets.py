from node import Node


class Epg(Node):

    def validate_append_relation(self, endp_dn):
        return 'prov' in endp_dn, "{} does not contain 'prov'".format(endp_dn)

    def validate_relation(self, endp):
        if isinstance(endp, Provision):
            return True, None
        return False, 'Relation should be Provision instance'


class Tenant(Node):

    def validate_append_relation(self, endp_dn):
        return 'contract' in endp_dn, "{} does not contain 'contract'".format(endp_dn)

    def validate_relation(self, endp):
        if isinstance(endp, Contract):
            return True, None
        return False, 'Relation should be Contract instance'


class Provision(Node):
    pass


class Contract(Node):
    pass
