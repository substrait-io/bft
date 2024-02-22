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

#### Local environment
Testing the dialects locally will require different frameworks/libraries. Following steps
mentions reference methods:
- **cuDF**  
   For testing functions in cuDF, a GPU powered system having RAPIDS/cuDF needs to be installed.
   Instructions on RAPIDS installation can be found [here](https://docs.rapids.ai/install)

   Alternatively, a Google Colab notebook with GPU can be used for testing. RAPIDS provides 
   a [template notebook](https://colab.research.google.com/drive/13sspqiEZwso4NYTbsflpPyNFaVAAxUgr) for installation and further usage. 

   ```
   import cudf
   a = cudf.Series([1, 2, 3])
   a.pow(2)  # Power function
   ```

- **Datafusion**  
   For testing with Datafusion, its CLI SQL console can be used. Installation instructions for various architectures can be found [here](https://arrow.apache.org/datafusion/user-guide/cli.html).
  ```
  $ datafusion-cli
  > select power(2,3);
  ```
- **DuckDB**  
  For testing with DuckDB, its CLI console or Python interface can be used. Installation instructions for various architectures and configuration can be found [here](https://duckdb.org/docs/installation/).
  ```
  $ duckdb
  D select pow(1,2);
  ```
- **Postgres**  
  The Postgres CLI can be utilized for testing. Instructions for installation on various architectures through installers, packages, or source code can be found [here](https://www.postgresql.org/download/).
  ```
  $ psql postgres
  postgres=# SELECT 2147483647::integer % 5;
  ```
- **SQLite**  
  SQLite testing can be conducted on the [CLI](https://sqlite.org/cli.html) after its [installation](https://www.sqlite.org/download.html).
  ```
  $ sqlite3 data.db
  sqlite> select pow(2,4);
  ```
- **Velox**  
 For testing with Velox, its Python interface can be installed via pip[https://pypi.org/project/pyvelox/].
  ```
  import pyvelox.pyvelox as pv
  expr = pv.Expression.from_string("power(a,4)")
  a = pv.from_list([1, 3])
  eval = expr.evaluate({"a":a})
  ```

#### CI environment
We perform continuous integration on a variety of systems to verify the integrity
of our dialect files and test cases.  For each test case a dialect file should
tell us how that system is expected to behave.  We then run the test case
against the system and verify the behavior is what we expected.

### The BFT Site

All of this information is rolled up into a website that serves as reference
documentation for these compute functions.  This is intended for consumption by
humans that wish to learn more details about specific functions.
