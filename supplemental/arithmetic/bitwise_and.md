# Bitwise_and

## Details

### Associative

The bitwise_and function is associative, i.e.
the grouping of operands does not affect the result. For example, 
bitwise_and(bitwise_and(a,b), c) will be same as bitwise_and(a, bitwise_and(b,c)).

### Commutative

The order of operands does not affect the result in Bitwise_and. For example, 
bitwise_and(a,b) will be the same as bitwise_and(b,a).

### Identity

For any valid integer, the bitwise_and with the bit pattern of all ones will result 
to itself. For example, bitwise_and(123, 111) = 123

### Bitwise Not Relationship

The result of performing a bitwise_and operation between a value 
x and its bitwise_not is always 0.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%] This is not
guaranteed to be true for integer subtraction when overflow is SILENT.
