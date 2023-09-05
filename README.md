# The B(ig) F(unction) T(axonomy)

The BFT aims to be a comprehensive catalogue of functions.  Functions are the
backbone of any compute system, but they are chronically under documented and often
full of corner cases whose behavior differs in various systems.  By documenting
exhaustively documenting these corner cases we hope to make it possible for systems
to fully describe their behaviors.  This will make it easier to know what problems
will be encountered switching between systems and, in some cases, make it possible
to obtain the correct behavior through expression transformation or a precise application
of function options.

## Major Concepts

The following concepts describe the various sources of information that the BFT
collects.

### Substrait

The BFT is an extension of (or perhaps a supplement to) [Substrait](https://substrait.io/).
We consider Substrait to be both a canonical source of function names as well as
a format for encoding function calls, including options.

However, Substrait is terse and does not go into lengthy descriptions of function
behavior.  It does not provide examples, motivation, or classification of functions.
As a result, the BFT starts with information from Substrait but then layers on additional
information from its own sources.

### Test Cases

The BFT includes a collection of test cases in the ```cases``` directory.  These
test cases explore different options, failure scenarios, or data types.  These
test cases are continuously verfied by running against different compute engines.

### Supplemental Information

The BFT includes more extensive prose documentation for functions.  It also can provide
information on the motivation behind functions, practical use cases for functions,
and a discussion of common properties that functions may have.  This information
is provided in the ```supplemental``` directory.

### Dialects

Most compute systems are not capable of satisfying the full range of functions and
options that are available.  Many compute systems are not capable of picking different
options.  The information in ```dialects``` represents facts about individual compute
engines that help us to understand how that system behaves.  For example, we list
which type classes a system supports and which options are implicitly specified when
a function is called in that system.

## Workflows

These workflows describe how this information is used.

### Dialect Testing

We perform continuous integration on a variety of systems to verify the integrity
of our dialect files and test cases.  For each test case a dialect file should
tell us how that system is expected to behave.  We then run the test case
against the system and verify the behavior is what we expected.

### The BFT Site

All of this information is rolled up into a website that serves as reference
documentation for these compute functions.  This is intended for consumption by
humans that wish to learn more details about specific functions.
