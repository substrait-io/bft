# Multiply

## Options

### Overflow

Multiplying two integers can trigger an overflow when the result is outside the
representable range of the type class. This option controls what happens when
this overflow occurs.

#### SILENT

If an overflow occurs then an integer value will be returned. The value is
undefined. It may be any integer and can change from engine to engine or
even from row to row within the same query.  The only constraint is that it
must be a valid value for the result type class (e.g. multiplying two int16
cannot yield an int32 on overflow)

#### SATURATE

If an overflow occurs then the largest (for positive overflow) or smallest
(for negative overflow) possible value for the type class will be returned.

#### ERROR

If an overflow occurs then an error should be raised.

### Rounding

Multiplying two floating point numbers can yield a result that is not exactly
representable in the given type class. In this case the value will be rounded.
Rounding behaviors are defined as part of the IEEE 754 standard.

#### TIE_TO_EVEN

Round to the nearest value. If the number is exactly halfway between two
values then round to the number whose least significant digit is even. Or,
because we are working with binary digits, round to the number whose last digit
is 0. This is the default behavior in many systems because it helps to avoid
bias in rounding.

#### TIE_AWAY_FROM_ZERO

Round to the nearest value. If the number is exactly halfway between two values
then round to the number furthest from zero.

#### TRUNCATE

Round to the nearest value. If the number is exactly halfway between two values
then round to the value closest to zero.

#### CEILING

Round to the value closest to positive infinity.

#### FLOOR

Round to the value closest to negative infinity.

## Details

### Other floating point exceptions

The IEEE 754 standard defines a number of exceptions beyond rounding. For
example, division by zero, overflow, and underflow. However, these exceptions
have default behaviors defined by IEEE 754 and, since no known engine deviates
from these default values, these exceptions are not exposed as options. For more
information on what happens in these cases refer to the IEEE 754 standard.

### Not commutative

Multiplication, the algebraic operation, is commutative.  So it may be tempting to
believe the multiply function is commutative as well.  However, this is not true
because of overflow.  For example, when working with int8 the result of
multiply(multiply(120, 10), -5) will yield a different result than
multiply(multiply(120, -5), 10) because the first will overflow and the second
will not.

## Properties

### Null propagating

If any of the inputs is null then the output will be null

### NaN propagating

If any of the inputs is NaN (and the other input is not null) then the output
will be NaN

### Stateless

The output will be the same regardless of the order of input rows. This is not
guaranteed to be true for integer multiplication when overflow is SILENT.
