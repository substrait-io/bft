# Factorial

## Options

### Overflow

Factorial being a function that may return a large value out of the permissible limit
of the type class can cause an overflow. This option helps
control the behavior upon overflow in the Factorial function.

#### SILENT

/[%Overflow$SILENT%]

#### SATURATE

/[%Overflow$SATURATE%]

#### ERROR

/[%Overflow$ERROR%]

## Details

### Input restrictions

Mathematically, factorial is not defined for negative integers or non-integer values, since it is essentially 
the reducing product of a given positive integer.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
