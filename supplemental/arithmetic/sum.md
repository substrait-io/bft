# Sum

## Options

### Overflow

Sum of a set of values can trigger an overflow when the result is outside the
representable range of the type class. This option controls what happens when
this overflow occurs.

#### SILENT

If an overflow occurs then an integer value will be returned. The value is
undefined. It may be any integer and can change from engine to engine or
even from row to row within the same query.  The only constraint is that it
must be a valid value for the result type class (e.g. adding two int16 cannot
yield an int32 on overflow)

#### SATURATE

If an overflow occurs then the largest (for positive overflow) or smallest
(for negative overflow) possible value for the type class will be returned.

#### ERROR

If an overflow occurs then an error should be raised.

## Details

### Other floating point exceptions

The IEEE 754 standard defines a number of exceptions beyond rounding. For
example, division by zero, overflow, and underflow. However, these exceptions
have default behaviors defined by IEEE 754 and, since no known engine deviates
from these default values, these exceptions are not exposed as options. For more
information on what happens in these cases refer to the IEEE 754 standard.

### Not commutative

Addition, the algebraic operation, is commutative.  So it may be tempting to
believe the add function is commutative as well.  However, this is not true because
of overflow.  For example, when working with int8 the result of
add(add(120, 10), -5) will yield a different result than add(add(120, -5), 10)
because the first will overflow and the second will not.

## Properties

### Nullability

Specifies how the nullability of output arguments are mapped to
input arguments. The Sum aggregate function follows a
DECLARED_OUTPUT nullability.

### Decomposable

The Sum aggregate function can be decomposed in more than
one intermediate steps.

### Intermediate

The intermediate output type of the Sum function is the
type class of the input arguments.
