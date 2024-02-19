# Bitwise_not

## Details

### Complementary

The bitwise not function behaves complimentary with itself, i.e. 
bitwise_not(bitwise_not(x)) will be equal to x, for any integer.

### XOR Relationship

Bitwise_not has a relationship with the XOR function, where the XORing of
a valid integer with the bit pattern of all 1s results in the bitwise_not of 
that integer.

### Two's complement

The bitwise_not of a valid integer is equivalent to negating the number and subtracting 1.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%] This is not
guaranteed to be true for integer subtraction when overflow is SILENT.
