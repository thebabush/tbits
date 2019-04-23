# TBits

Three-valued bits and bitvectors for python 3, including per-bit taint data.

Idea taken from [Rolf Rolles](https://www.msreverseengineering.com).

## Install

`pip install git+https://github.com/thebabush/tbits`

## Example

```py
import tbits

# Create a 8-bit bit vector
abc = tbits.tbits('ABC', 8)

# T[X{A},X{B},X{C},O,O,O,O,O]
print(abc)

# T[X{A},X{B},X{C,A},X{C,A,B},X{C,A,B},X{C,A,B},O,O]
print(abc * tbits.TBitVector.from_integer(0b101, 8))

# T[O,O,X{A},X{B},X{C},O,O,O]
print(abc * tbits.TBitVector.from_integer(0b100, 8))

# T[X{A},O,X{C,x},O,O,O,O,O]
print(abc & tbits.tbits('10x', 8))

# TODO: use `x` as value instead of reference? This would make `x ^ x == 0` true.
# For now, though...
# T[X{x}]
print(tbits.tbits('x') ^ tbits.tbits('x'))

x = tbits.tbits('x', 1)
# T[O]
print(x ^ x)

# False
print(abc.is_concrete())

# T[X{t0},X{t1},X{t2},X{t3},X{t4},X{t5},X{t6},X{t7}]
print(tbits.TBitVector.from_unknown(8))

# T[X{t8},X{t9},X{tA},X{tB},X{tC},X{tD},X{tE},X{tF}]
print(tbits.TBitVector.from_unknown(8))

# 7
print(abc.x2i())

# T[X{a},X{b},X{c},X{c},X{c},X{c},X{c},X{c}]
print(tbits.tbits('abc', 3).sx(8))
```

