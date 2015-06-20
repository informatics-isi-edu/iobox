# Beanbag (*draft*)

Beanbag is a profile and extension of the simple hierarchical
packaging file format BagIt defined by the IETF draft specification
[The BagIt File Packaging Format (V0.97)](https://tools.ietf.org/html/draft-kunze-bagit-10).

## BagIt

Structure of a standard BagIt:

    <base directory>/
    |  bagit.txt
    |  manifest-<algorithm>.txt
    |  [optional additional tag files]
    \--- data/
          | [payload files]
    \--- [optional tag directories]/
          | [optional tag files]

### Optional: `fetch.txt`

Among the standard BagIt optional additional tag files is the `fetch.txt` file.
The contents of which are:

    URL LENGTH FILENAME

This allows the bag to include references to files rather than include the
entire contents of files in the payload section. See the formal specification
for details.

## Beanbag profile

The beanbag profile adds the following elements to the base
specification.

* Beanbag metadata tag file
* Table data files subdirectory
* Asset data files subdirectory
* Schema tag directory

Structure of the *Beanbag* profile of the *BagIt* specification:

    <base directory>/
    |  bagit.txt
    |  manifest-<algorithm>.txt
    |  beanbag.txt
    |  [optional additional tag files]
    \--- data/
          \--- tables/
                | [optional <schema-table-name>.csv files]
          \--- assets/
                | [optional asset data files]
          | [optional payload files]
    \--- schema/
          | [optional <schema-name>.json files]
          | [and/or <table-name>.json files]
    \--- [optional tag directories]/
          | [optional tag files]

### Element: `beanbag.txt`

The `beanbag.txt` must contain the following fields.

    Beanbag version: <version-number>

Where `version-number` should match the version of the *beanbag* file
specification followed.

### Element: `data/tables/`

The `data/tables/` subdirectory may contain optional table data files. These
files are expected in comma-separate values (CSV) format with the following
encoding rules.

1. They must be encoded in UTF-8
1. The first row must be a header row
1. Values must be separated by a comma (,) character
1. Values that need escaping must be escaped by single quotes (') character
1. Each row of values must be terminated by a carriage return (CR) character

The table files (i.e., CSV files) must be named `schema-table-name.csv` where
`schema` is a subpart of the name used to scope the namespace for the `table`
name.

### Element: `data/assets/`

The `data/assets/` subdirectory may contain optional asset data files. Assets
may be any file format and are treated as opaque binary objects.

### Element: `schema/`

The `schema` subdirectory may contain option schema representation files. These
files describe the schema for the `table` data files. The schema representation
must be encoded in JavaScript Object Notation (JSON) format. The *beanbag* file
must include:

1. One or more `<schema-name>.json` files; and/or
2. One or more `schema-table-name>.json` files.

The schema description file(s) must describe the schema for all table files
included in the `data/tables/` subdirectory.

Example `<schema-name>.json`:  

*TODO* insert example here. This will be exactly what comes out of ERMrest.

Example `<schema-table-name>.json`:  

*TODO* insert example here. This will be exactly what comes out of ERMrest.

## Notes

This is a *draft* specification.

The *beanbag* file should probably have a required tag file for *provenance* at
the top level that includes information on author and timestamp at least.

The table data could be generalized to support alternative representations of
"structured" or "metadata" files.

Alternatively, the `tables` and `assets` subdirectories could be abandoned in
favor of flattening all files under `data` and including a custom tag file that
indicates which data files should be treated like metadata and which should be
treated like assets (i.e., objects).
