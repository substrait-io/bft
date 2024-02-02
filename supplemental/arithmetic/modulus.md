# Modulus

## Options
Not supported 

### Overflow

Not supported

### Rounding

Not supported

### Division_type

Determines the nature of division rounding function and quotient
evaluation that shall lead to the reminder. The reminder will be
determined by  r = x - round_func(x/y)

#### TRUNCATE

The quotient is evaluated i.e. the round_func(x/y) is truncated,
thus the fractional result is rounded towards zero.

#### FLOOR

The quotient is evaluated i.e. the round_func(x/y) is floored,
thus the fractional result is rounded to the largest integer
value less than or equal to it.

### On_domain_error

Option controls what happens when the dividend is ±infinity or
the divisor is 0 or ±infinity in a divide function.

#### NULL

Return a NULL if the dividend is ±infinity or the divisor is 0
or ±infinity.

#### ERROR

If the dividend is ±infinity or the divisor is 0 or ±infinity,
an error should be raised.

## Details
 
### Overflow and rounding
The Modulus function will not require options such as Overflow
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
