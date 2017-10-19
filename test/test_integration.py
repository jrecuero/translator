# import sys
# import pytest
#
# src_path = '.'
# sys.path.append(src_path)

# from db import DB, get_db
import pytest
from translator.db import DB
from translator.node import Node


EPG_1 = '/uni/epg/1'
EPG_2 = '/uni/epg/2'
EPG_3 = '/uni/epg/3'
EPG_4 = '/uni/epg/4'

PROV_1 = '/uni/prov/1'
PROV_2 = '/uni/prov/2'


@pytest.fixture
def dbase():
    db = DB()
    Node.DB = db
    return db


@pytest.fixture(params=[[EPG_1, EPG_2, EPG_3, EPG_4]])
def epgs(request, dbase):
    epg_list = []
    for x in request.param:
        epg_list.append(Node(x))
    return epg_list


@pytest.fixture
def provs():
    return []


class TestIntegration(object):

    @pytest.mark.xfail(strict=True, raises=AssertionError)
    def test_no_dbase(self):
        Node(EPG_1)

    @pytest.mark.xfail(strict=True, raises=AssertionError)
    def test_no_dn(self, dbase):
        Node("")

    def test_create_epgs(self, dbase, epgs, provs):
        assert dbase.find(EPG_1) == epgs[0]
        assert dbase.find(EPG_2) == epgs[1]
        assert dbase.find(EPG_3) == epgs[2]
        assert dbase.find(EPG_4) == epgs[3]
        for x in epgs:
            assert x.rs_relations is None
            assert x.rt_relations == []

    @pytest.mark.parametrize('prov', [PROV_1, ])
    @pytest.mark.parametrize('epgs', [[EPG_1, ], ], indirect=True)
    def test_add_rs_relations_no_prov(self, prov, dbase, epgs, provs):
        # Create Rs-Relation without Prov
        epgs[0].add_rs_relation(prov)
        assert Node.get_class_rs_relations() == [[prov, epgs[0]]]
        assert epgs[0].rs_relations is not None
        assert not epgs[0].rs_relations.state
        assert epgs[0].rs_relations.dn == prov

        # Create Prov
        node1 = Node(prov)
        provs.append(node1)
        assert Node.get_class_rs_relations() == []
        assert epgs[0].rs_relations.state
        assert epgs[0].rs_relations.dn == prov
        assert len(provs[0].rt_relations) == 1
        assert provs[0].rt_relations[0].dn == EPG_1
        assert provs[0].rt_relations[0].state

    @pytest.mark.parametrize('epgs', [[EPG_1, EPG_2, EPG_3, ]], indirect=True)
    def test_add_rs_relations(self, dbase, epgs, provs):
        # Create Rs-Relation without Prov
        epgs[0].add_rs_relation(PROV_1)
        assert Node.get_class_rs_relations() == [[PROV_1, epgs[0]]]
        assert epgs[0].rs_relations is not None
        assert not epgs[0].rs_relations.state
        assert epgs[0].rs_relations.dn == PROV_1

        # Create Prov
        node1 = Node(PROV_1)
        provs.append(node1)
        assert Node.get_class_rs_relations() == []
        assert epgs[0].rs_relations.state
        assert epgs[0].rs_relations.dn == PROV_1
        assert len(provs[0].rt_relations) == 1
        assert provs[0].rt_relations[0].dn == EPG_1
        assert provs[0].rt_relations[0].state

        # Create Rs-Relation with Prov
        node2 = Node(PROV_2)
        provs.append(node2)
        epgs[1].add_rs_relation(PROV_2)
        assert Node.get_class_rs_relations() == []
        assert epgs[1].rs_relations.state
        assert epgs[1].rs_relations.dn == PROV_2
        assert len(provs[1].rt_relations) == 1
        assert provs[1].rt_relations[0].dn == EPG_2
        assert provs[1].rt_relations[0].state

        # Create Rs-Relation with Same Prov
        epgs[2].add_rs_relation(PROV_2)
        assert Node.get_class_rs_relations() == []
        assert epgs[2].rs_relations.state
        assert epgs[2].rs_relations.dn == PROV_2
        assert len(provs[1].rt_relations) == 2
        assert provs[1].rt_relations[0].dn == EPG_2
        assert provs[1].rt_relations[0].state
        assert provs[1].rt_relations[1].dn == EPG_3
        assert provs[1].rt_relations[1].state

        # Delete Prov
        provs[1].delete()
        del provs[1]
        assert len(Node.get_class_rs_relations()) == 2
        assert Node.get_class_rs_relations() == [[PROV_2, epgs[1]], [PROV_2, epgs[2]]]
        assert not epgs[1].rs_relations.state
        assert epgs[1].rs_relations.dn == PROV_2
        assert not epgs[2].rs_relations.state
        assert epgs[2].rs_relations.dn == PROV_2

        # Re-Create Prov
        node2 = Node(PROV_2)
        provs.append(node2)
        assert Node.get_class_rs_relations() == []
        assert epgs[1].rs_relations.state
        assert epgs[1].rs_relations.dn == PROV_2
        assert epgs[2].rs_relations.state
        assert epgs[2].rs_relations.dn == PROV_2
        assert len(provs[1].rt_relations) == 2
        assert epgs[1].rs_relations.state
        assert epgs[1].rs_relations.dn == PROV_2
        assert epgs[2].rs_relations.state
        assert epgs[2].rs_relations.dn == PROV_2
        assert provs[1].rt_relations[0].dn == EPG_2
        assert provs[1].rt_relations[0].state
        assert provs[1].rt_relations[1].dn == EPG_3
        assert provs[1].rt_relations[1].state

        # Delete EPG
        epgs[2].delete()
        del epgs[2]
        assert len(provs[1].rt_relations) == 1
        assert provs[1].rt_relations[0].dn == EPG_2
        assert provs[1].rt_relations[0].state

        # Update prov
        epgs[0].rs_relations.updates == []
        provs[0].update('update/prov/1')
        epgs[0].rs_relations.updates == ['update/prov/1']

        # Update epg
        provs[0].rt_relations[0].updates == []
        epgs[1].update('update/epg/1')
        provs[0].rt_relations[0].updates == ['update/epg/1']

        # Delete EPG without PROV
        provs[0].delete()
        del provs[0]
        assert Node.get_class_rs_relations() == [[PROV_1, epgs[0]]]
        assert not epgs[0].rs_relations.state
        assert epgs[0].rs_relations.dn == PROV_1
        epgs[0].delete()
        del epgs[0]
        assert Node.get_class_rs_relations() == []
        assert dbase.find(EPG_1) is None
        assert dbase.find(PROV_1) is None
        assert len(epgs) == 1
        assert len(provs) == 1
