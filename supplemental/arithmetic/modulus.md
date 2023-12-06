# Modulus

## Options
Not supported 

### Overflow

Not supported

### Rounding

Not supported

## Details
 
### Overflow and rounding
The Modulus function will not require options such as Overflow or rounding
which are present in other arithmetic functions, because there will not be
an event in the allowed kernels and data type where the modulus function can
behave in one of such ways. Modulus function is defined for integer values only
and they do not operate on floating values. Thus, they cannot have floats as
remainders. Additionally, result of modulus on two operands will always result 
a value within the range.

### Not commutative

Modulus as an arithmetic operation is not commutative by nature.

## Properties

### Null propagating

If any of the inputs is null then the output will be null

### NaN propagating

If any of the inputs is NaN (and the other input is not null) then the output
will be NaN

### Stateless

The output will be the same regardless of the order of input rows. This is not
guaranteed to be true for integer division when overflow is SILENT.
