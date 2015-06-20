# IObox

IObox is a collection of Extract, Transform, Load (ETL) utilities for
ERMrest+Hatrac.

# Summary

The utilities in this project are generally categorized under extract,
transform, or load.

* Extract: These utilities connect to a data source (or read from a file) and
generate a data "bag".
* Transform: These utilities take a "bag" run transformations and output an
updated "bag".
* Load: These utilities take a "bag" and load it into a data sink.

# Data Format

The data format produced by, transformed by, or consumed by the IObox utilities
is described in the [data package specification (draft)](./docs/bags.md).

# Design

See the minimally specified [conceptual design](./docs/design.md).
