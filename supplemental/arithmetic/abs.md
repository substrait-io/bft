# Abs

## Options

### Overflow

Computing the absolute of integer values may result in overflow due to unevenness of two's complement.
This option helps control the behavior of the function when the input goes out of permissible range 
of the type class.

#### SILENT

/[%Overflow$SILENT%]

#### SATURATE

/[%Overflow$SATURATE%]

#### ERROR

/[%Overflow$ERROR%]

## Details

### Non multiplicative

Although the mathematical operation for Absolute value is multiplicative, but the function is not
due to overflow. For example, for int8, abs(-1 * -128) will not be the same as 
abs(-1) * abs(-128), since the former will cause an overflow.

### Triangular Inequality

Mathematically, the absolute operation has the triangular inequality, i.e. for two real numbers, 
x & y, abs(x+y) <= abs(x) + abs(y). This might not hold true for the abs function due to overflow.
For example, for int8, abs(-127 + 1) will not be the same as abs(-127) + abs(1), since the 
latter will overflow.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
