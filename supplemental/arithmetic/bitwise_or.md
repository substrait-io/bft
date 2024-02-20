# Bitwise_or

## Details

### Associative

The bitwise_or function is associative, i.e.
the grouping of operands does not affect the result. For example, 
bitwise_or(bitwise_or(a,b), c) will be same as bitwise_or(a, bitwise_or(b,c)).

### Commutative

The order of operands does not affect the result in Bitwise_or. For example, 
bitwise_or(a,b) will be the same as bitwise_or(b,a).

### Identity

For any valid integer, the bitwise_or with zero will result 
to itself. For example, bitwise_or(123, 000) = 123

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
