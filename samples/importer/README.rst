Sample Project for CLI Importer
-------------------------------

NetBeans / Maven project framework for the `CLI importer` project.


Contents
~~~~~~~~

A stub implementation for the `XLSX Extractor` module can be found in ``XlsxInputStreamExtractor.java``. A reference design of the `CSV Extractor` can be found in the same package under the name ``XlsxInputStreamExtractor.java``.

.. code-block:

    src
    └── main
        └── java
            └── org
                └── datagator
                    └── tools
                        └── importer
                            └── impl
                                ├── CsvInputStreamExtractor.java
                                └── XlsxInputStreamExtractor.java


CLI Invocation
~~~~~~~~~~~~~~

.. code-block::

    $ java -jar target/datagator-tools-0.0.6.jar -h
    Usage: importer [-F <filter>] [-h] [-L <int>,<int>]
    -F,--filter <filter>      specify grouping filter as /<foo>/<bar>
    -h,--help                 show this help message
    -L,--layout <int>,<int>   specify matrix layout as
    <columnHeaders>,<rowHeaders>

.. code-block::

    $ java -jar target/datagator-tools-0.0.6.jar -L 1,3 ../../data/raw/Dyadic_Combined_Sample.csv
    {"kind": "datagator#Matrix", "columnHeaders": 1, "rowHeaders": 3, "rows": [[...]], "rowsCount": 100, "columnsCount": 87}
