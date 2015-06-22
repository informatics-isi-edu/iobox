# Beanbag Format (*draft*)

*Beanbag* is a profile for using *BagIt*, a simple hierarchical packaging file
format defined by IETF draft [The BagIt File Packaging Format (V0.97)][BagIt].

## BagIt Structure

Structure of a standard *BagIt*:

    <base directory>/
    |  bagit.txt
    |  manifest-<algorithm>.txt
    |  [optional additional tag files]
    \--- data/
          | [payload files]
    \--- [optional tag directories]/
          | [optional tag files]

### Fetch Files: `fetch.txt`

*BagIt* allows for files in the manifest to be contained within the package or
externally referenced in the optional `fetch.txt` tag file. The format of
`fetch.txt` is:

    URL LENGTH FILENAME

This allows the bag to include references to files rather than include the
entire contents of files in the payload section. See the formal specification
for details.

## Beanbag Profile

*Beanbag* is a profile for using the *BagIt* file specification. Packages
that conform to the *Beanbag* profile are valid *BagIt* packages as well.

### Summary

* *Beanbag*-specific bag metadata
* Optional schema description of payload files
* Recommend URL-encoding of payload file names
* Recommend `text/csv` payload files follow [RFC 4180]


### Package Structure

Structure of the *Beanbag* profile of the *BagIt* specification:

    <base directory>/
    |  bagit.txt
    |  bag-info.txt
    |  manifest-<algorithm>.txt
    |  tagmanifest-<algorithm>.txt
    |  schema.json
    |  [optional additional tag files]
    \--- data/
          | [optional payload files]
    \--- [optional tag directories]/
          | [optional tag files]

**Note** that `schema.json` is the only new tag file specified by the *Beanbag*
profile.

### Beanbag Metadata: `bag-info.txt`

*BagIt* allows for optional bag metadata in the `bag-info.txt` tag file.
*Beanbag* packages should include the following bag metadata.

    Beanbag-version: <version-number>

Where `version-number` should match the version of the *Beanbag* profile used by
the package.

### Tag Manifest: `tagmanifest-<algorithm>.txt`

*BagIt* specifies an optional manifest file for tag files in the
`tagmanifest-<algorithm>.txt` file. *Beanbag* packages that contain the optional
schema description file `schema.json` must include the *BagIt* tag file
manifest.

### Recommended URL-encoded Filenames

In addition to the *BagIt* requirement for UTF-8 encoding, payload file names
should also be URL-encoded per [RFC 1738].

### Recommended `text/csv` Formatting

The *Beanbag* profile recommends the use of [RFC 4180] for `text/csv` typed
payload files, also known as Comma-Separated Values (CSV) files. In addition to
RFC 4180, this profile also recommends the following.

1. The header row MUST be present with column names that exactly match the
   model described in the optional schema tag file.

2. The entire file MUST be UTF-8 encoded and each quoted or unquoted field value
   MUST be a valid UTF-8 sequence, i.e. field separator, record separator,
   quoted string delimiter, or end of file MUST NOT follow an incomplete
   multi-byte character.

### Schema Description: `schema.json`

A *Beanbag* package may contain an optional schema description in the
`schema.json` file. The schema references and describes the structure of payload
files contained in the package (or referenced by the `fetch.txt` tag file). A
schema description should only be considered *internally consistent* within the
*Beanbag* package. There are no guarantees regarding the relationship of the
schema to any external data or systems.

In the current draft of *Beanbag*, the schema may be used to describe the
structure of `text/csv` payload files. The structure includes the expected
column headers, the column header types, the relationship of columns to other
columns in the same CSV file or in other CSV files, and the relationship of
columns to other payload data files included or referenced in the package.

An incomplete example follows. Suppose the payload of a *Beanbag* package
included the following `text/csv` file.

```
data/foo/bar.csv
```

The corresponding schema description (`schema.json`) file could describe it as
follows.

```javascript
{ "schemas": [
  { "name": "foo" }
    "tables": [
      { "name": "bar.csv",
         "columns": [
           { "name": "a_column",
             "type": "int64" },
              ...
      ]},
      ...
  ]},
  ...
]}
```

In the example, the schema named `foo` maps to the directory `data/foo` and its
table `bar.csv` maps to the file named `data/foo/bar.csv`. From the example,
`bar.csv` should include a header row with a column named `a_column` which
contains UTF-8 encoded values within the `int64` numeric value range.

# Notes

This is a *draft* specification.

The *Beanbag* profile should provide recommendations for including provenance.

[BagIt]: https://tools.ietf.org/html/draft-kunze-bagit-10 "The BagIt File Packaging Format (V0.97)"
[RFC 1738]: http://www.ietf.org/rfc/rfc1738.txt "RFC 1738"
[RFC 4180]: http://www.ietf.org/rfc/rfc4180.txt "RFC 4180"
