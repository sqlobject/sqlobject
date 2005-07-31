from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Joins
########################################

class PersonJoiner(SQLObject):

    name = StringCol(length=40, alternateID=True)
    addressJoiners = RelatedJoin('AddressJoiner')

class AddressJoiner(SQLObject):

    zip = StringCol(length=5, alternateID=True)
    personJoiners = RelatedJoin('PersonJoiner')

class ImplicitJoiningSO(SQLObject):
    foo = RelatedJoin('Bar')

class ExplicitJoiningSO(SQLObject):
    foo = MultipleJoin('Bar', joinMethodName='foo')

class TestJoin:

    def setup_method(self, meth):
        setupClass(PersonJoiner)
        setupClass(AddressJoiner)
        for n in ['bob', 'tim', 'jane', 'joe', 'fred', 'barb']:
            PersonJoiner(name=n)
        for z in ['11111', '22222', '33333', '44444']:
            AddressJoiner(zip=z)

    def test_join(self):
        b = PersonJoiner.byName('bob')
        assert b.addressJoiners == []
        z = AddressJoiner.byZip('11111')
        b.addAddressJoiner(z)
        self.assertZipsEqual(b.addressJoiners, ['11111'])
        self.assertNamesEqual(z.personJoiners, ['bob'])
        z2 = AddressJoiner.byZip('22222')
        b.addAddressJoiner(z2)
        self.assertZipsEqual(b.addressJoiners, ['11111', '22222'])
        self.assertNamesEqual(z2.personJoiners, ['bob'])
        b.removeAddressJoiner(z)
        self.assertZipsEqual(b.addressJoiners, ['22222'])
        self.assertNamesEqual(z.personJoiners, [])

    def assertZipsEqual(self, zips, dest):
        assert [a.zip for a in zips] == dest

    def assertNamesEqual(self, people, dest):
        assert [p.name for p in people] == dest

    def test_joinAttributeWithUnderscores(self):
        # Make sure that the implicit setting of joinMethodName works
        assert hasattr(ImplicitJoiningSO, 'foo')
        assert not hasattr(ImplicitJoiningSO, 'bars')

        # And make sure explicit setting also works
        assert hasattr(ExplicitJoiningSO, 'foo')
        assert not hasattr(ExplicitJoiningSO, 'bars')

class PersonJoiner2(SQLObject):

    name = StringCol('name', length=40, alternateID=True)
    addressJoiner2s = MultipleJoin('AddressJoiner2')

class AddressJoiner2(SQLObject):

    class sqlmeta:
        defaultOrder = ['-zip', 'plus4']

    zip = StringCol(length=5)
    plus4 = StringCol(length=4, default=None)
    personJoiner2 = ForeignKey('PersonJoiner2')

class TestJoin2:

    def setup_method(self, meth):
        setupClass([PersonJoiner2, AddressJoiner2])
        p1 = PersonJoiner2(name='bob')
        p2 = PersonJoiner2(name='sally')
        for z in ['11111', '22222', '33333']:
            a = AddressJoiner2(zip=z, personJoiner2=p1)
            #p1.addAddressJoiner2(a)
        AddressJoiner2(zip='00000', personJoiner2=p2)

    def test_basic(self):
        bob = PersonJoiner2.byName('bob')
        sally = PersonJoiner2.byName('sally')
        assert len(bob.addressJoiner2s) == 3
        assert len(sally.addressJoiner2s) == 1
        bob.addressJoiner2s[0].destroySelf()
        assert len(bob.addressJoiner2s) == 2
        z = bob.addressJoiner2s[0]
        z.zip = 'xxxxx'
        id = z.id
        del z
        z = AddressJoiner2.get(id)
        assert z.zip == 'xxxxx'

    def test_defaultOrder(self):
        p1 = PersonJoiner2.byName('bob')
        assert ([i.zip for i in p1.addressJoiner2s]
                == ['33333', '22222', '11111'])

