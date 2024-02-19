# Sqrt

## Options

### Rounding

Taking the square root of an input can yield a result that is not exactly
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

### On_domain_error

Square root operation is typically allowed only for non-negative real numbers. This option controls the behavior when the function is called with values not adhering to this rule.

#### NAN

/[%On_domain_error$NAN%]

#### ERROR

/[%On_domain_error$ERROR%]

## Details

### Other floating point exceptions

The IEEE 754 standard defines a number of exceptions beyond rounding. For
example, division by zero, overflow, and underflow. However, these exceptions
have default behaviors defined by IEEE 754 and, since no known engine deviates
from these default values, these exceptions are not exposed as options. For more
information on what happens in these cases refer to the IEEE 754 standard.

### Domain restrictions

Mathematically, square root function for negative real numbers results to complex numbers, and thus in function usage, typically only positive real numbers are allowed. Applying the function on a negative real number may raise an Error or result in a NaN value.


## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%] This is not guaranteed to be true for integer addition when overflow is SILENT.
