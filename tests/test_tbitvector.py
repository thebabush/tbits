from tbits import TBit, tbit, TBitVector, tbits
import random


o = tbits('0', 2)
i = tbits('1', 2)
x = tbits('x', 2)
y = tbits('y', 2)
oo = tbits('00')
io = tbits('01')
xo = tbits('0x')
oi = tbits('10')
ii = tbits('11')
xi = tbits('1x')
ox = tbits('x0')
oy = tbits('y0')
ix = tbits('x1')
xx = tbits('xx')


def eq_bits(aa, bb):
    for a, b in zip(aa._tbits, bb._tbits):
        if a.O and not b.O:
            return False
        elif a.I and not b.I:
            return False
        elif a.X and not b.X:
            return False
    return True


def test_tyte():
    for i in range(16):
        assert int(TBitVector.from_integer(i, 4)) == i


def test_xor():
    assert eq_bits(oo ^ oo, oo)
    assert eq_bits(oi ^ oo, oi)
    assert eq_bits(oi ^ io, ii)
    assert eq_bits(ox ^ oo, ox)
    assert eq_bits(xx ^ io, xx)


def test_add():
    assert eq_bits(oo + oi, oi)
    assert eq_bits(oo + ox, ox)
    assert eq_bits(ox + ox, xo)
    assert eq_bits(oy + ox, xx)


def test_sub():
    assert eq_bits(x - o, x)

    # Some random tests :)
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        assert int(TBitVector.from_integer(a, 8) - TBitVector.from_integer(b, 8)) == (a - b) % 256


def test_mul():
    # Some random tests :)
    for _ in range(100):
        a = random.randint(-255, 255)
        b = random.randint(-255, 255)
        assert int(TBitVector.from_integer(a, 8) * TBitVector.from_integer(b, 8)) == (a * b) % 256


def test_div():
    # Some random tests :)
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(1, 255)
        assert int(TBitVector.from_integer(a, 8) / TBitVector.from_integer(b, 8)) == a // b


def test_mod():
    # Some random tests :)
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(1, 255)
        assert int(TBitVector.from_integer(a, 8) % TBitVector.from_integer(b, 8)) == a % b

    t = xx % io
    assert eq_bits(t, ox)
    assert t[0] == xx[0]


def test_approx():
    assert oo.x2o() == 0
    assert oo.x2i() == 0
    assert oi.x2o() == 1
    assert oi.x2i() == 1
    assert xx.x2i() == 3
    assert xx.x2o() == 0


def test_shift():
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        assert int(TBitVector.from_integer(a, 8) << TBitVector.from_integer(b, 8)) == (a << b) & 0xFF
        assert int(TBitVector.from_integer(a, 8) >> TBitVector.from_integer(b, 8)) == (a >> b) & 0xFF


def test_rot():
    ox = tbits('x', 8)
    xo = tbits('0x', 8)
    assert eq_bits(tbits('1', 8).rotl(tbits('1', 8)), tbits('01', 8))
    assert eq_bits(ox.rotl(TBitVector.from_integer(8, 8)), ox)
    assert eq_bits(ox.rotl(TBitVector.from_integer(9, 8)), xo)
    assert eq_bits(ox.rotr(TBitVector.from_integer(8, 8)), ox)
    assert eq_bits(ox.rotr(TBitVector.from_integer(9, 8)), tbits('0000000x', 8))


def test_ge():
    for _ in range(100):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = TBitVector.from_integer(a, 8) >= TBitVector.from_integer(b, 8)
        assert not c.X
        c = True if c.I else False
        assert c == (a >= b)

