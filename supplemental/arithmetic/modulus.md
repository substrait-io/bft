# Modulus

## Options

### Overflow

The modulus operation typically occurs after finding the quotient,
i.e., mod(x, y) = x - round_func(x/y), where the round_func can be
to truncate, floor, or any such operation. Thus, the entire operation
may trigger an overflow when the result is outside the representable
range of the type class. This option controls what happens when this overflow occurs.

#### SILENT

If an overflow occurs then an integer value will be returned. The value is
undefined. It may be any integer and can change from engine to engine or
even from row to row within the same query.  The only constraint is that it
must be a valid value for the result type class (e.g. modulus of int16
cannot yield an int32 on overflow)

#### SATURATE

If an overflow occurs then the largest (for positive overflow) or smallest
(for negative overflow) possible value for the type class will be returned.

#### ERROR

If an overflow occurs then an error should be raised.

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
 
### Overflow

The Modulus function requires the Overflow option in situations
where any or all of the involved operations result in overflow
from the specified range. For example, in mod(-128, -1) within
the int8 range, an overflow will occur as the operation will
lead to (-128) - round_func(-128/-1). Since the division operation
(-128/-1) results in an overflow (given that the range of int8
is -127 to 128), the Overflow option becomes essential.

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
