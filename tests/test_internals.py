from sqlakeyset import OC, Paging, Page
from pytest import raises

from sqlakeyset import serialize_bookmark

from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import nullslast


def test_oc():
    a = asc('a')
    b = desc('a')
    c = asc('b')
    n = nullslast(desc('a'))

    a = OC(a)
    b = OC(b)
    c = OC(c)
    n = OC(n)

    assert str(a) == str(OC('a'))
    assert a.is_ascending
    assert not b.is_ascending
    assert not n.reversed.reversed.is_ascending
    assert str(a.element) == str(b.element) == str(n.element)
    assert str(a) == str(b.reversed)
    assert str(n.reversed.reversed) == str(n)

    assert a.name == 'a'
    assert n.name == 'a'
    assert n.quoted_full_name == 'a'
    assert repr(n) == '<OC: a DESC NULLS LAST>'


def test_paging_objects():
    p = Page(['abc'])
    assert p.one() == 'abc'

    with raises(RuntimeError):
        Page([1, 2]).one()

    with raises(RuntimeError):
        Page([]).one()

    def general_asserts(p):
        if not p.backwards:
            assert p.further == p.next
        else:
            assert p.further == p.previous

        if not p.has_further:
            assert p.current_opposite == (None, not p.backwards)

        assert p.is_full == (len(p.rows) >= p.per_page)
        assert p.bookmark_further == \
            serialize_bookmark(p.further)

    def getitem(row, order_cols):
        return tuple(row[c.name] for c in order_cols)

    ob = [OC(x) for x in ['id', 'b']]

    T1 = []

    T2 = [
        {'id': 1, 'b': 2},
        {'id': 2, 'b': 1},
        {'id': 3, 'b': 3}
    ]

    p = Paging(T1, 10, ob, backwards=False, current_marker=None, get_marker=getitem)
    assert p.next == (None, False)
    assert p.further == (None, False)
    assert p.previous == (None, True)
    assert not p.is_full
    general_asserts(p)

    p = Paging(T2, 3, ob, backwards=False, current_marker=None, get_marker=getitem)
    assert p.next == ((3, 3), False)
    assert not p.has_next
    assert not p.has_previous
    assert p.further == ((3, 3), False)
    assert p.previous == ((1, 2), True)
    assert p.is_full
    general_asserts(p)

    p = Paging(T2, 2, ob, backwards=False, current_marker=None, get_marker=getitem)
    assert p.next == ((2, 1), False)
    assert p.has_next
    general_asserts(p)

    assert not p.has_previous
    assert p.previous == ((1, 2), True)

    assert p.further == ((2, 1), False)

    general_asserts(p)
