# Divide

## Options

### Overflow

Dividing two integers can trigger an overflow when the result is outside the
representable range of the type class. This option controls what happens when
this overflow occurs.

#### SILENT

If an overflow occurs then an integer value will be returned. The value is
undefined. It may be any integer and can change from engine to engine or
even from row to row within the same query.  The only constraint is that it
must be a valid value for the result type class (e.g. dividing two int16
cannot yield an int32 on overflow)

#### SATURATE

If an overflow occurs then the largest (for positive overflow) or smallest
(for negative overflow) possible value for the type class will be returned.

#### ERROR

If an overflow occurs then an error should be raised.

### Rounding

Dividing two floating point numbers can yield a result that is not exactly
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

### On domain error

Option controls what happens when the dividend and divisor in a divide function
are either both 0 or both ±infinity.

#### NAN

Return a Not a Number value if the dividend and the divisor are either both 0 or
both ±infinity.

#### ERROR

If the dividend and the divisor are either both 0 or both ±infinity an error should 
be raised.

### On division by zero

Option controls function behavior in cases when the divisor is 0 but the dividend is not zero.

#### LIMIT

Return +infinity or -infinity depending on the signs of the dividend and the divisor involved.

## Details

### Other floating point exceptions

The IEEE 754 standard defines a number of exceptions beyond rounding. For
example, overflow, and underflow. However, these exceptions
have default behaviors defined by IEEE 754 and, since no known engine deviates
from these default values, these exceptions are not exposed as options. For more
information on what happens in these cases refer to the IEEE 754 standard.

### Not commutative

Division, the algebraic operation, is commutative.  So it may be tempting to
believe the divide function is commutative as well.  However, this is not true
because of overflow.  For example, when working with int8 the result of
divide(divide(-128, -1), -1) will yield a different result than
divide(-128, divide(-1, -1)) because the first will overflow and the second
will not.

## Properties

### Null propagating

If any of the inputs is null then the output will be null

### NaN propagating

If any of the inputs is NaN (and the other input is not null) then the output
will be NaN

### Stateless

The output will be the same regardless of the order of input rows. This is not
guaranteed to be true for integer division when overflow is SILENT.
