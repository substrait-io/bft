# Tan

## Options

### Rounding

Tangent of an input can yield a result that is not exactly
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

### Numerical Precision

The precision of the tan function depends on the architecture in various dialects.

### Output Range

Mathematically, the tangent function has a range [-Inf, Inf], since it is undefined and approaches
infinity in input values of (pi/2) + k*pi, where k is any integer. Computationally, the inputs
where the tangent function is not defined results in approximately 1255.76 or -1255.76. Thus,
the output range becomes [-1255.76, 1255.76].

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
