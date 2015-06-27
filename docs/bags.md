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

*BagIt* allows for optional bag metadata in the `bag-info.txt` tag file.  This file must be included in a *Beanbag* bag.  The following standard metadata tags are required.

    Bagging-Date  Date (YYYY-MM-DD) that the content was prepared for delivery.

    Internal-Sender-Identifier  An alternate sender-specific identifier for the content and/or bag.  This value should be a GUID in URI format. The name does not have to be resolvable.
    
*COMMENT: The Internal-Sender-Identifer should be modeled after the URI-A specification in the OAI specfication. WHen the bag is holding and OAI aggregate, the Internal-Sender-Identifier should be the URI-A.

> A URI-A MUST be a protocol-based URI. However, an Aggregation is a conceptual construct, and thus it does not have a Representation. In contrast, a Resource Map that asserts the Aggregation does have a Representation in which  that assertion is made available to clients and agents. The Cool URIs for the Semantic Web guidlines are adopted to support discovery of the HTTP URI of the asserting Resource Map given the HTTP URI of an Aggregation. Details about the mechanisms of access are described in ORE User Guide - HTTP Implementation.
*

In addition, *Beanbag* packages should include the following bag metadata.

    Beanbag-version: <version-number>

Where `version-number` should match the version of the *Beanbag* profile used by
the package.

#### Optional metadata

    Lineage: URI
    
The value of this attribute is the Internal-Sender-Identifier of any bags from which the data in the current bag was derived.  This should corrispond to the lineage realationship in OAI.  TODO: Need to specifify behavoir of multiplie items, a list or set?

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

It has suggested that we may want to track origional URL for files that are included in the bag. This might be something like a fetched.txt which would be in the same format as the fetch.txt file, but would also apply to files that are currently located in the data directory.  Alternatively, this information might be included in per-asset metadata that would be included in an OAI compliented metadata file.


[BagIt]: https://tools.ietf.org/html/draft-kunze-bagit-11 "The BagIt File Packaging Format (V0.97)"
[RFC 1738]: http://www.ietf.org/rfc/rfc1738.txt "RFC 1738"
[RFC 4180]: http://www.ietf.org/rfc/rfc4180.txt "RFC 4180"
