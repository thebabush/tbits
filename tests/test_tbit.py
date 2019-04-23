from tbits import TBit, tbit


o = tbit(0)
i = tbit(1)
x = tbit('x')
y = tbit('y')


def test_and():
    assert o & o == o
    assert o & i == o
    assert o & x == o
    assert i & o == o
    assert i & i == i
    assert i & x == x
    assert x & o == o
    assert x & i == x
    t = x & y
    assert t.tag == {'x', 'y'}

    assert x & x == x


def test_or():
    assert o | o == o
    assert o | i == i
    assert o | x == x
    assert i | o == i
    assert i | i == i
    assert i | x == i
    assert x | o == x
    assert x | i == i
    t = x | y
    assert t.tag == {'x', 'y'}

    assert x | x == x


def test_xor():
    assert o ^ o == o
    assert o ^ i == i
    assert o ^ x == x
    assert i ^ o == i
    assert i ^ i == o
    t = i ^ y
    assert t.tag == {'y'}
    assert x ^ o == x
    t = y ^ i
    assert t.tag == {'y'}
    t = x ^ y
    assert t.tag == {'x', 'y'}

    assert (x ^ x).O


def test_invert():
    assert ~o == i
    assert ~i == o
