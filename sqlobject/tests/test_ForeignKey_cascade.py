from sqlobject import ForeignKey, SQLObject, StringCol, \
    SQLObjectIntegrityError, SQLObjectNotFound
from sqlobject.tests.dbtest import raises, setupClass


class SOTestPerson1(SQLObject):
    name = StringCol()


class SOTestMessageCascadeTrue(SQLObject):
    sender = ForeignKey('SOTestPerson1', cascade=True)
    recipient = ForeignKey('SOTestPerson1', cascade=True)
    body = StringCol()


def test1():
    setupClass([SOTestPerson1, SOTestMessageCascadeTrue])

    john = SOTestPerson1(name='john')
    emily = SOTestPerson1(name='emily')
    message = SOTestMessageCascadeTrue(
        sender=emily, recipient=john, body='test1'
    )

    SOTestPerson1.delete(emily.id)
    john.expire()
    message.expire()

    john.sync()
    raises(SQLObjectNotFound, emily.sync)
    raises(SQLObjectNotFound, message.sync)


class SOTestPerson2(SQLObject):
    name = StringCol()


class SOTestMessageCascadeFalse(SQLObject):
    sender = ForeignKey('SOTestPerson2', cascade=False)
    recipient = ForeignKey('SOTestPerson2', cascade=False)
    body = StringCol()


def test2():
    setupClass([SOTestPerson2, SOTestMessageCascadeFalse])

    john = SOTestPerson2(name='john')
    emily = SOTestPerson2(name='emily')
    message = SOTestMessageCascadeFalse(
        sender=emily, recipient=john, body='test2'
    )

    raises(SQLObjectIntegrityError, SOTestPerson2.delete, emily.id)
    john.expire()
    emily.expire()
    message.expire()

    john.sync()
    emily.sync()
    message.sync()

    assert message.sender == emily
    assert message.recipient == john


class SOTestPerson3(SQLObject):
    name = StringCol()


class SOTestMessageCascadeNull(SQLObject):
    sender = ForeignKey('SOTestPerson3', cascade='null')
    recipient = ForeignKey('SOTestPerson3', cascade='null')
    body = StringCol()


def test3():
    setupClass([SOTestPerson3, SOTestMessageCascadeNull])

    john = SOTestPerson3(name='john')
    emily = SOTestPerson3(name='emily')
    message = SOTestMessageCascadeNull(
        sender=emily, recipient=john, body='test3'
    )

    SOTestPerson3.delete(emily.id)
    john.expire()
    message.expire()

    john.sync()
    message.sync()
    raises(SQLObjectNotFound, emily.sync)

    assert message.sender is None
    assert message.recipient == john

    SOTestPerson3.delete(john.id)
    john.expire()
    message.expire()

    message.sync()
    raises(SQLObjectNotFound, john.sync)

    assert message.recipient is None


class SOTestPerson4(SQLObject):
    name = StringCol()


class SOTestMessageCascadeMixed(SQLObject):
    sender = ForeignKey('SOTestPerson4', cascade=True)
    recipient = ForeignKey('SOTestPerson4', cascade='null')
    body = StringCol()


def test4():
    setupClass([SOTestPerson4, SOTestMessageCascadeMixed])

    john = SOTestPerson4(name='john')
    emily = SOTestPerson4(name='emily')
    message = SOTestMessageCascadeMixed(
        sender=emily, recipient=john, body='test4'
    )

    SOTestPerson4.delete(emily.id)
    john.expire()
    message.expire()

    john.sync()
    raises(SQLObjectNotFound, message.sync)


def test5():
    setupClass([SOTestPerson4, SOTestMessageCascadeMixed])

    john = SOTestPerson4(name='john')
    emily = SOTestPerson4(name='emily')
    message = SOTestMessageCascadeMixed(
        sender=emily, recipient=john, body='test5'
    )

    john.destroySelf()
    emily.expire()
    message.expire()

    emily.sync()
    message.sync()

    assert message.recipient is None
    assert message.sender == emily
