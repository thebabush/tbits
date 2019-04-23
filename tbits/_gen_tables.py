from ._tbits import _zero, _one


def _bit_add(b0, b1, b2):
    if b0.O and b1.O and b2.O:
        return _zero, _zero
    elif b0.O and b1.O and b2.I:
        return _one, _zero
    elif b0.O and b1.O and b2.X:
        return b2, _zero
    elif b0.O and b1.I and b2.O:
        return _one, _zero
    elif b0.O and b1.I and b2.I:
        return _zero, _one
    elif b0.O and b1.I and b2.X:
        return (~b2), b2
    elif b0.O and b1.X and b2.O:
        return b1, _zero
    elif b0.O and b1.X and b2.I:
        return (~b1), b1
    elif b0.O and b1.X and b2.X:
        return (b1 ^ b2), (b1 & b2)
    elif b0.I and b1.O and b2.O:
        return _one, _zero
    elif b0.I and b1.O and b2.I:
        return _zero, _one
    elif b0.I and b1.O and b2.X:
        return (~b2), b2
    elif b0.I and b1.I and b2.O:
        return _zero, _one
    elif b0.I and b1.I and b2.I:
        return _one, _one
    elif b0.I and b1.I and b2.X:
        return b2, _one
    elif b0.I and b1.X and b2.O:
        return (~b1), b1
    elif b0.I and b1.X and b2.I:
        return b1, _one
    elif b0.I and b1.X and b2.X:
        return (~(b1 ^ b2)), (b1 | b2)
    elif b0.X and b1.O and b2.O:
        return b0, _zero
    elif b0.X and b1.O and b2.I:
        return (~b0), b0
    elif b0.X and b1.O and b2.X:
        return (b0 ^ b2), (b0 & b2)
    elif b0.X and b1.I and b2.O:
        return (~b0), b0
    elif b0.X and b1.I and b2.I:
        return b0, _one
    elif b0.X and b1.I and b2.X:
        return (~(b0 ^ b2)), (b0 | b2)
    elif b0.X and b1.X and b2.O:
        return (b0 ^ b1), (b0 & b1)
    elif b0.X and b1.X and b2.I:
        return (~(b0 ^ b1)), (b0 | b1)
    elif b0.X and b1.X and b2.X:
        return (b0 ^ b1 ^ b2), ((b0 & b1) | (b2 & (b0 ^ b1)))
    else:
        raise Exception('_bit_add: Unhandled case "{}"'.format(b0, b1, b2))
