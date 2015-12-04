#
# Copyright 2015 University of Southern California
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module includes a utility for converting an ERMrest schema document into
a graphviz dot file.
"""

import sys
import json


def schema2dot(schemata):
    """
    Converts a schemata document into a graphviz dot document.

    Arguments:
     - 'schema' must be a json formatted schemata document per the ERMrest
    specification.

    Returns: A string, the contents of which are a graphviz dot document.
    """
    edges = []
    dot = """
digraph schemata {
    ratio="fill";
    node [style=rounded];
"""

    # for each schema, create a numbered subgraph cluster
    cluster_count = 0
    schemas = schemata['schemas']
    for schema_name in schemas:
        schema = schemas[schema_name]
        dot += """
    subgraph cluster_%d {
        label="%s"
""" % (cluster_count, schema_name)

        # for each table, add a node to the current subgraph
        tables = schema['tables']
        for table_name in tables:
            fqname = schema_name + ":" + table_name
            table = tables[table_name]
            dot += """
        "%(name)s" [shape=record, fontsize=14, label="{%(label)s|\\
""" % dict(name=fqname, label=table_name)

            # list the columns
            columns = table['column_definitions']
            for column in columns:
                dot += """
            %s \\l\\
""" % column['name']

            # list the keys (may be composite keys)
            for key in table['keys']:
                dot += """
            KEY (%s) \\l\\
""" % ", ".join(key['unique_columns'])

            # record the foreign key references as edges (add to graph later)
            for fk in table['foreign_keys']:
                rc = fk['referenced_columns']
                edge = dict(tail=fqname,
                            head=rc[0]['schema_name'] + ":" + rc[0]['table_name'],
                            label="(%s) -> (%s)" % (
                                    ", ".join(fkc['column_name'] for fkc in fk['foreign_key_columns']),
                                    ", ".join(rc['column_name'] for rc in fk['referenced_columns']) )
                            )
                edges.append(edge)

            dot += """
        }"]
"""

        dot += """
    }
"""
        cluster_count += 1

    # add the edges to the graph
    dot += """
    edge[arrowtail=crow, arrowhead=none, dir=both, label=""];
"""
    for edge in edges:
        dot += "    \"%(tail)s\" -> \"%(head)s\" [label=\"%(label)s\"]\n" % edge

    # close the graph
    dot += """
}
"""
    return dot


def main(argv):
    """
    Expected to run as the main routine of this module.

    Arguments:
     - 'argv[0]' must be the filename of a file that contains text that can be
    desearialized into a json document of an ERMrest schemata.

    Returns:
     - 0 success
     - 1 usage error
     - 2 other failure
    """
    if len(argv) != 2:
        sys.stderr.write("usage: %s schema_document.json\n" % argv[0])
        return 1

    try:
        f = open(argv[1])
        dot = schema2dot(json.load(f))
    except Exception, te:
        sys.stderr.write("failed: %s\n" % str(te))
        return 2

    sys.stdout.write(dot)
    return 0
