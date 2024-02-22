# Power

## Options

### Overflow

The power operation may lead to overflowing when the result is 
outside the representable range of the type class. 
This option controls what happens when this overflow occurs.

#### SILENT

/[%Overflow$SILENT%]

#### SATURATE

/[%Overflow$SATURATE%]

#### ERROR

/[%Overflow$ERROR%]

## Details
 
### Overflow

The power function requires the Overflow control for situations where
the resulting value exceeds the type class limit. For example, in 
pow(2, 65), although the input values are in the allowed int64 range, 
but the result goes out of range. 

### Numerical Precision

The precision of the power function depends on the precision of the input types
and the way the operation is carried out in various dialects.

## Properties

### Null propagating

/[%Properties$Null_propagating%]

### NaN propagating

/[%Properties$NaN_propagating%]

### Stateless

/[%Properties$Stateless%]
