# Negate

## Options

### Overflow

Negating a number on the limit of the allowed range of the type class may lead to 
overflowing. For example, if we have consider for i8, negate(-128), then the result
will overflow since the range for the int8 type class is [-128,127]. This option helps
control the behavior upon overflow in the negate function.

#### SILENT

/[%Overflow$SILENT%]

#### SATURATE

/[%Overflow$SATURATE%]

#### ERROR

/[%Overflow$ERROR%]

## Details

### Not Idempotent

While the algebraic operation is Idempotent, but the function is not, because of Overflow.
For example, with in8, the result of negate(negate(-128)) will not be -128 as this will overflow.

### Not commutative

Negation, the algebraic operation, is commutative.  So it may be tempting to
believe the add function is commutative as well.  However, this is not true because
of overflow.  For example, when working with int8 the result of
negate(124 + 4) will yield a different result than negate(124) + negate(4)
because the first will overflow and the second will not.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
