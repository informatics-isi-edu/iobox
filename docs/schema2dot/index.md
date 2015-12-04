The `schema2dot` utility converts a schema document (as specified by ERMrest)
into a graphviz _dot_ formatted document.

### Prerequisites
* Python 2.6 or higher
* Graphviz (to convert to PDF; optional)

### Installation
From the source distribution base directory, run:
  ```
  # python setup.py install
  ```

### Usage
From the command line, run:
  ```
  $ schema2dot a_schema_doc.json
  ```

It will write its output to _stdout_ which you may redirect to a _.dot_ file.

To convert the dot file to a pdf, use graphviz:
   ```
   $ dot -Tpdf schema.dot -o schema.pdf
   ```
For more information on graphviz go to: http://graphviz.org
