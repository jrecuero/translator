import sys
import pytest

src_path = '.'
sys.path.append(src_path)

from db import get_db
from node import Node


EPG_1 = '/uni/epg/1'
EPG_2 = '/uni/epg/2'
EPG_3 = '/uni/epg/3'

PROV_1 = '/uni/prov/1'
PROV_2 = '/uni/prov/2'


class TestIntegration(object):

    @pytest.fixture(autouse=True)
    def init(self):
        self.epgs = []
        self.provs = []

        node1 = Node(EPG_1)
        self.epgs.append(node1)
        node2 = Node(EPG_2)
        self.epgs.append(node2)
        node3 = Node(EPG_3)
        self.epgs.append(node3)

    def test_create_epgs(self):
        assert get_db().find(EPG_1) == self.epgs[0]
        assert get_db().find(EPG_2) == self.epgs[1]
        assert get_db().find(EPG_3) == self.epgs[2]
        for x in self.epgs:
            assert x.rs_relations is None
            assert x.rt_relations == []

    def test_add_rs_relations(self):
        # Create Rs-Relation without Prov
        self.epgs[0].add_rs_relation(PROV_1)
        assert Node.get_rs_relations() == [[PROV_1, self.epgs[0]]]
        assert self.epgs[0].rs_relations is not None
        assert not self.epgs[0].rs_relations.state
        assert self.epgs[0].rs_relations.dn == PROV_1

        # Create Prov
        node1 = Node(PROV_1)
        self.provs.append(node1)
        assert Node.get_rs_relations() == []
        assert self.epgs[0].rs_relations.state
        assert self.epgs[0].rs_relations.dn == PROV_1
        assert len(self.provs[0].rt_relations) == 1
        assert self.provs[0].rt_relations[0].dn == EPG_1
        assert self.provs[0].rt_relations[0].state

        # Create Rs-Relation with Prov
        node2 = Node(PROV_2)
        self.provs.append(node2)
        self.epgs[1].add_rs_relation(PROV_2)
        assert Node.get_rs_relations() == []
        assert self.epgs[1].rs_relations.state
        assert self.epgs[1].rs_relations.dn == PROV_2
        assert len(self.provs[1].rt_relations) == 1
        assert self.provs[1].rt_relations[0].dn == EPG_2
        assert self.provs[1].rt_relations[0].state

        # Create Rs-Relation with Same Prov
        self.epgs[2].add_rs_relation(PROV_2)
        assert Node.get_rs_relations() == []
        assert self.epgs[2].rs_relations.state
        assert self.epgs[2].rs_relations.dn == PROV_2
        assert len(self.provs[1].rt_relations) == 2
        assert self.provs[1].rt_relations[0].dn == EPG_2
        assert self.provs[1].rt_relations[0].state
        assert self.provs[1].rt_relations[1].dn == EPG_3
        assert self.provs[1].rt_relations[1].state

        # Delete Prov
        self.provs[1].delete()
        del self.provs[1]
        assert len(Node.get_rs_relations()) == 2
        assert Node.get_rs_relations() == [[PROV_2, self.epgs[1]], [PROV_2, self.epgs[2]]]
        assert not self.epgs[1].rs_relations.state
        assert self.epgs[1].rs_relations.dn == PROV_2
        assert not self.epgs[2].rs_relations.state
        assert self.epgs[2].rs_relations.dn == PROV_2

        # Re-Create Prov
        node2 = Node(PROV_2)
        self.provs.append(node2)
        assert Node.get_rs_relations() == []
        assert self.epgs[1].rs_relations.state
        assert self.epgs[1].rs_relations.dn == PROV_2
        assert self.epgs[2].rs_relations.state
        assert self.epgs[2].rs_relations.dn == PROV_2
        assert len(self.provs[1].rt_relations) == 2
        assert self.epgs[1].rs_relations.state
        assert self.epgs[1].rs_relations.dn == PROV_2
        assert self.epgs[2].rs_relations.state
        assert self.epgs[2].rs_relations.dn == PROV_2
        assert self.provs[1].rt_relations[0].dn == EPG_2
        assert self.provs[1].rt_relations[0].state
        assert self.provs[1].rt_relations[1].dn == EPG_3
        assert self.provs[1].rt_relations[1].state

        # Delete EPG
        self.epgs[2].delete()
        del self.epgs[2]
        assert len(self.provs[1].rt_relations) == 1
        assert self.provs[1].rt_relations[0].dn == EPG_2
        assert self.provs[1].rt_relations[0].state

        # Update prov
        self.epgs[0].rs_relations.updates == []
        self.provs[0].update('update/prov/1')
        self.epgs[0].rs_relations.updates == ['update/prov/1']

        # Update epg
        self.provs[0].rt_relations[0].updates == []
        self.epgs[1].update('update/epg/1')
        self.provs[0].rt_relations[0].updates == ['update/epg/1']

        # Delete EPG without PROV
        self.provs[0].delete()
        del self.provs[0]
        assert Node.get_rs_relations() == [[PROV_1, self.epgs[0]]]
        assert not self.epgs[0].rs_relations.state
        assert self.epgs[0].rs_relations.dn == PROV_1
        self.epgs[0].delete()
        del self.epgs[0]
        assert Node.get_rs_relations() == []
        assert get_db().find(EPG_1) is None
        assert get_db().find(PROV_1) is None
        assert len(self.epgs) == 1
        assert len(self.provs) == 1
