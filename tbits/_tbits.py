import itertools


class TBit(object):
    @property
    def O(self):
        return False

    @property
    def I(self):
        return False

    @property
    def X(self):
        return False

    @classmethod
    def _check(cls, other):
        assert isinstance(other, TBit)

    def __and__(self, b):
        self._check(b)
        a = self
        if a.O and b.O:
            return _zero
        elif a.O and b.I:
            return _zero
        elif a.O and b.X:
            return _zero
        elif a.I and b.O:
            return _zero
        elif a.I and b.I:
            return _one
        elif a.I and b.X:
            return b
        elif a.X and b.O:
            return _zero
        elif a.X and b.I:
            return a
        elif a.X and b.X:
            if a == b:
                return a
            else:
                return join(a, b)

    def __or__(self, b):
        self._check(b)
        a = self
        if a.O and b.O:
            return _zero
        elif a.O and b.I:
            return _one
        elif a.O and b.X:
            return b
        elif a.I and b.O:
            return _one
        elif a.I and b.I:
            return _one
        elif a.I and b.X:
            return _one
        elif a.X and b.O:
            return a
        elif a.X and b.I:
            return _one
        elif a.X and b.X:
            if a == b:
                return a
            else:
                return join(a, b)

    def __xor__(self, b):
        self._check(b)
        a = self
        if a.O and b.O:
            return _zero
        elif a.O and b.I:
            return _one
        elif a.O and b.X:
            return b
        elif a.I and b.O:
            return _one
        elif a.I and b.I:
            return _zero
        elif a.I and b.X:
            return b.copy()
        elif a.X and b.O:
            return a
        elif a.X and b.I:
            return a.copy()
        elif a.X and b.X:
            if a == b:
                return _zero
            else:
                return join(a, b)

    def __invert__(self):
        if self.O:
            return _one
        elif self.I:
            return _zero
        else:
            return self.copy()

    def __repr__(self):
        return self.__str__()

    @property
    def p(self):
        assert 1 == 0


class _TBitZero(TBit):
    @property
    def O(self):
        return True

    def __str__(self):
        return 'O'


class _TBitOne(TBit):
    @property
    def I(self):
        return True

    def __str__(self):
        return 'I'


class _TBitX(TBit):
    def __init__(self, tag):
        assert isinstance(tag, frozenset)
        self._tag = tag

    @property
    def X(self):
        return True

    @property
    def tag(self):
        return self._tag

    def __str__(self):
        return 'X{' + ','.join(self._tag) + '}'

    def copy(self):
        return _TBitX(self.tag)


_zero = _TBitZero()
_one = _TBitOne()

# Needs to be here because of super "clever" recursive import
from . import _gen_tables


def join(a, b):
    return tbit(a.tag.union(b.tag))


def tbit(arg):
    if arg == 0:
        return _zero
    elif arg == 1:
        return _one
    else:
        if isinstance(arg, str):
            arg = frozenset([arg])
        elif isinstance(arg, set):
            arg = frozenset(arg)
        assert isinstance(arg, frozenset)

        return _TBitX(arg)


def tbits(s, size=None):
    if not size:
        size = len(s)
    elif size < len(s):
        s = s[:size]
    assert size > 0

    tt = []
    for c in s:
        if c == '0' or c == '1':
            tt.append(tbit(int(c)))
        else:
            tt.append(tbit(c))
    if len(tt) < size:
        tt += [tbit(0)] * (size - len(tt))
    return TBitVector(tuple(tt))


class TBitVector(object):
    _unknown_counter = 0

    def __init__(self, tbits):
        self._tbits = tbits

    @classmethod
    def from_integer(self, i, size):
        assert size > 0
        if i < 0:
            i = i % (1 << size)
        acc = []
        for _ in range(size):
            b = i & 1
            i >>= 1
            acc.append(tbit(b))
        return TBitVector(tuple(acc))

    @classmethod
    def from_unknown(cls, size):
        assert size > 0
        tbits = []
        for i in range(size):
            tbits.append(tbit('t{:X}'.format(cls._unknown_counter)))
            cls._unknown_counter += 1
        return TBitVector(tuple(tbits))

    @property
    def size(self):
        return len(self._tbits)

    def __str__(self):
        return 'T[' + ','.join(map(str, self._tbits)) + ']'

    def __repr__(self):
        return self.__str__()

    def __xor__(self, other):
        assert self.size == other.size
        return TBitVector(tuple(a ^ b for a, b in zip(self._tbits, other._tbits)))

    def __and__(self, other):
        assert self.size == other.size
        return TBitVector(tuple(a & b for a, b in zip(self._tbits, other._tbits)))

    def __or__(self, other):
        assert self.size == other.size
        return TBitVector(tuple(a | b for a, b in zip(self._tbits, other._tbits)))

    def __invert__(self):
        return TBitVector(tuple(~a for a in self._tbits))

    def is_concrete(self):
        return not any(a.X for a in self._tbits)

    def __int__(self):
        assert self.is_concrete()
        acc = 1 if self._tbits[-1].I else 0
        for b in reversed(self._tbits[:-1]):
            acc <<= 1
            acc |= 1 if b.I else 0
        return acc

    def __add__(self, other):
        assert self.size == other.size
        aa = self._tbits
        bb = other._tbits
        ss = []
        c = _zero
        for a, b in zip(aa, bb):
            s, c = _gen_tables._bit_add(a, b, c)
            ss.append(s)
        return TBitVector(tuple(ss))

    def __sub__(self, other):
        assert self.size == other.size

        # This pass is basically a dumb heuristics to make results closer to the truth (useful for mod)
        aa = []
        bb = []
        for a, b in zip(self._tbits, other._tbits):
            # if a and b are the same thing, we can already make a decision
            if a == b:
                aa.append(_zero)
                bb.append(_zero)
            else:
                aa.append(a)
                bb.append(b)

        # Compute normal __sub__ (an add with flipped b and initial carry set to 1)
        ss = []
        c = _one
        for a, b in zip(aa, bb):
            s, c = _gen_tables._bit_add(a, ~b, c)
            ss.append(s)
        return TBitVector(tuple(ss))

    def _get_concrete_bits(self):
        return TBitVector(tuple(tbit(1) if b.I else tbit(0) for b in self._tbits))

    def _get_unknown_bits(self):
        return TBitVector(tuple(b if b.X else tbit(0) for b in self._tbits))

    def __lshift__(self, offset):
        if isinstance(offset, int):
            assert offset >= 0
            if offset == 0:
                return self
            elif offset >= self.size:
                return TBitVector((tbit(0),) * self.size)
            return TBitVector(tuple([tbit(0)] * offset + list(self._tbits[:-offset])))
        elif isinstance(offset, TBitVector):
            # First take care of known values
            tmp = self << int(offset._get_concrete_bits())
            uu = offset._get_unknown_bits()
            for i, u in enumerate(uu):
                if u.X:
                    shift = 1 << i
                    shifted = tmp << shift
                    # Y = UNK & SHIFTED_BIT + NOT(UNK) & BIT
                    # + <=> disjoint OR
                    tmp = TBitVector(tuple((u & b).disjoint_or((~u) & a) for a, b in zip(tmp._tbits, shifted._tbits)))
            return tmp
        else:
            raise Exception('Wrong argument type: {}'.format(type(offset)))

    def __rshift__(self, offset):
        if isinstance(offset, int):
            assert offset >= 0
            if offset == 0:
                return self
            elif offset >= self.size:
                return TBitVector((tbit(0),) * self.size)
            bits = list(self._tbits)
            return TBitVector(tuple(bits[offset:] + [tbit(0)] * offset))
        elif isinstance(offset, TBitVector):
            # First take care of known values
            tmp = self >> int(offset._get_concrete_bits())
            uu = offset._get_unknown_bits()
            for i, u in enumerate(uu):
                if u.X:
                    shift = 1 << i
                    shifted = tmp >> shift
                    # Y = UNK & SHIFTED_BIT + NOT(UNK) & BIT
                    # + <=> disjoint OR
                    tmp = TBitVector(tuple((u & b).disjoint_or((~u) & a) for a, b in zip(tmp._tbits, shifted._tbits)))
            return tmp
        else:
            raise Exception('Wrong argument type: {}'.format(type(offset)))

    def rotl(self, b):
        assert isinstance(b, TBitVector)
        # TODO: Special case for integer b
        mod = TBitVector.from_integer(b.size, b.size)
        size = TBitVector.from_integer(self.size, self.size)
        return self << (b % mod) | self >> ((size - b) % mod)

    def rotr(self, b):
        assert isinstance(b, TBitVector)
        # TODO: Special case for integer b
        mod = TBitVector.from_integer(b.size, b.size)
        size = TBitVector.from_integer(self.size, self.size)
        return self >> (b % mod) | self << ((size - b) % mod)

    def __mul__(self, other):
        # Note: surprisingly, the dumb/slow version works for both signed and unsigned ints (module 2**size)
        # TODO: special case for integer constants
        # TODO: special case for power of 2
        # TODO: faster (karatsuba?)
        assert isinstance(other, TBitVector)
        assert self.size == other.size
        ss = TBitVector.from_integer(0, self.size)
        for i in range(self.size):
            if self._tbits[i].I:
                ss += other
            elif self._tbits[i].X:
                ss += other & TBitVector((self._tbits[i],) * other.size)
            other <<= 1
        return ss

    def possible_values_big(self, stop=100):
        subs = {}
        tbits = list(self._tbits)
        counter = 0
        for i, t in enumerate(tbits):
            if t.X:
                subs[i] = counter
                counter += 1

        counter = 0
        vals = set()
        for ss in itertools.product((0, 1), repeat=len(subs)):
            tt = []
            for i, t in enumerate(tbits):
                if t.X:
                    tt.append(tbit(ss[subs[i]]))
                else:
                    tt.append(t)
            vals.add(int(TBitVector(tuple(tt))))

            counter += 1
            if counter >= stop:
                break

        if not vals:
            vals = {int(self)}
        return vals

    def possible_values_small(self, stop=100):
        subs = {}
        tbits = list(self._tbits)
        counter = 0
        for t in tbits:
            if t.X and t not in subs:
                subs[t] = counter
                counter += 1

        counter = 0
        vals = set()
        for ss in itertools.product((0, 1), repeat=len(subs)):
            tt = []
            for t in tbits:
                if t in subs:
                    tt.append(tbit(ss[subs[t]]))
                else:
                    tt.append(t)
            vals.add(int(TBitVector(tuple(tt))))

            counter += 1
            if counter >= stop:
                break

        if not vals:
            vals = {int(self)}
        return vals

    def sx(self, new_size):
        assert new_size >= self.size
        return TBitVector(tuple(list(self._tbits) + [self._tbits[-1]] * (new_size - self.size)))

    def zx(self, new_size):
        assert new_size >= self.size
        return TBitVector(tuple(list(self._tbits) + [tbit(0)] * (new_size - self.size)))

    def ix(self, new_size):
        assert new_size >= self.size
        return TBitVector(tuple(list(self._tbits) + [tbit(1)] * (new_size - self.size)))

    def __neg__(self):
        return (~self) + TBitVector.from_integer(1, self.size)

    def __getitem__(self, k):
        if isinstance(k, int):
            return self._tbits[k]
        elif isinstance(k, slice):
            return TBitVector(self._tbits.__getitem__(k))
        else:
            raise Exception('Unsupported __getitem__ arg type: {}'.format(type(k)))

    def __mod__(self, b):
        assert self.size == b.size

        # Needs a mask because symbolic values ruin the higher bits
        # TODO: Figure out if there's some way to do mod without this problem
        for zeros_a, x in enumerate(reversed(self._tbits)):
            if x.X or x.I:
                break
        for zeros_b, y in enumerate(reversed(b._tbits)):
            if y.X or y.I:
                break
        zeros = max(zeros_a, zeros_b)
        mask = TBitVector((_one,) * (self.size - zeros) + (_zero,) * zeros)

        return self._div_not_zero(b)[1] & mask

    def __floordiv__(self, b):
        return self / b

    def __truediv__(self, b):
        assert self.size == b.size
        return self._div_not_zero(b)[0]

    def _div_not_zero(self, D):
        N = self
        Q = []
        R = TBitVector.from_integer(0, self.size)
        for i in range(self.size - 1, -1, -1):
            R <<= 1
            R = list(R._tbits)
            R[0] = N[i]
            R = TBitVector(tuple(R))

            c = R >= D
            cc = TBitVector((c,) * self.size)
            R = R - (cc & D)

            Q.append(c)

        return TBitVector(tuple(Q[::-1])), R

    def x2i(self):
        return int(TBitVector(tuple(b if b.O else _one for b in self._tbits)))

    def x2o(self):
        return int(TBitVector(tuple(b if b.I else _zero for b in self._tbits)))

    def __ge__(self, b):
        assert isinstance(b, TBitVector)
        a = self
        if a.x2o() >= b.x2i():
            return _one
        elif a.x2i() < b.x2o():
            return _zero

        # CF | ZF
        c = a.ix(a.size + 1) - b.zx(b.size + 1)  # r >= b
        if c[:-1].is_concrete() and int(c[:-1]) == 0:
            c = _one
        else:
            c = c[-1]
        return c
