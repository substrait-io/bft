# Subtract

## Options

### Overflow

Subtracting two integers can trigger an overflow when the result is outside the
representable range of the type class. This option controls what happens when
this overflow occurs.

#### SILENT

/[%Overflow$SILENT%] For e.g. subtracting two int16 cannot
yield an int32 on overflow.

#### SATURATE

/[%Overflow$SATURATE%]

#### ERROR

/[%Overflow$ERROR%]

### Rounding

Subtracting two floating point numbers can yield a result that is not exactly
representable in the given type class. In this case the value will be rounded.
Rounding behaviors are defined as part of the IEEE 754 standard.

#### TIE_TO_EVEN

/[%Rounding$TIE_TO_EVEN%]

#### TIE_AWAY_FROM_ZERO

/[%Rounding$TIE_AWAY_FROM_ZERO%]

#### TRUNCATE

/[%Rounding$TRUNCATE%]

#### CEILING

/[%Rounding$CEILING%]

#### FLOOR

/[%Rounding$FLOOR%]

## Details

### Other floating point exceptions

The IEEE 754 standard defines a number of exceptions beyond rounding. For
example, division by zero, overflow, and underflow. However, these exceptions
have default behaviors defined by IEEE 754 and, since no known engine deviates
from these default values, these exceptions are not exposed as options. For more
information on what happens in these cases refer to the IEEE 754 standard.

### Not commutative

Subtraction, the algebraic operation, is commutative.  So it may be tempting to
believe the subtract function is commutative as well.  However, this is not true
because of overflow.  For example, when working with int8 the result of
subtract(subtract(-120, 10), -5) will yield a different result than
subtract(subtract(-120, -5), 10) because the first will overflow and the second
will not.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%] This is not
guaranteed to be true for integer subtraction when overflow is SILENT.
