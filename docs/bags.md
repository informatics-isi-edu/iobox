# Beanbag Format (*draft*)

_This is a draft specification under development._

*Beanbag* is a profile for using *BagIt*, a simple hierarchical packaging file
format defined by IETF draft [The BagIt File Packaging Format (V0.97)][BagIt].

## BagIt Structure

The layout of a standard *BagIt* package:

```
    <base directory>/
    |  bagit.txt
    |  manifest-<algorithm>.txt
    |  [optional additional tag files]
    \--- data/
          | [payload files]
          \ ...
    \--- [optional tag directories]/
          | [optional tag files]
          \ ...
```

### Fetch Files: `fetch.txt`

*BagIt* allows for files in the manifest to be contained within the package or
externally referenced in the optional `fetch.txt` tag file. The format of
`fetch.txt` is:

```
    URL LENGTH FILENAME
```

This allows the bag to include references to files rather than include the
entire contents of files in the payload section. See the formal specification
for details.

## Beanbag Profile

*Beanbag* is a profile for using the *BagIt* file specification. Packages
that conform to the *Beanbag* profile are valid *BagIt* packages as well. The
usage of BagIt

### Summary

* *Beanbag*-specific bag metadata
* Optional schema description of payload files
* Recommend URL-encoding of payload file names
* Recommend `text/csv` payload files follow [RFC 4180]


### Package Structure

Structure of the *Beanbag* profile of the *BagIt* specification:

```
    <base directory>/
    |  bagit.txt
    |  bag-info.txt
    |  manifest-<algorithm>.txt
    |  tagmanifest-<algorithm>.txt
    |  [optional additional tag files]
    \--- data/
          | [optional payload files]
          \ ...
    \--- [optional tag directories]/
          | [optional tag files]
          \ ...
```

### Beanbag Metadata: `bag-info.txt`

*BagIt* allows for optional bag metadata in the `bag-info.txt` tag file.  This
file must be included in a *Beanbag* bag.  The following standard metadata tags
are required.

    Bagging-Date: ISO 8601 Date

    Internal-Sender-Identifier: URI

An alternate sender-specific identifier for the content and/or bag.  This value
should be a GUID in URI format. The name does not have to be resolvable as it is
possible for a bag to never exist as a information resource.

COMMENT: The Internal-Sender-Identifer should be modeled after the URI-A
specification in the OAI specification. When the bag is holding an OAI aggregate,
the Internal-Sender-Identifier should be the URI-A.

> A URI-A MUST be a protocol-based URI. However, an Aggregation is a conceptual
> construct, and thus it does not have a Representation. In contrast, a Resource
> Map that asserts the Aggregation does have a Representation in which  that
> assertion is made available to clients and agents. The Cool URIs for the
> Semantic Web guidelines are adopted to support discovery of the HTTP URI of
> the asserting Resource Map given the HTTP URI of an Aggregation. Details about
> the mechanisms of access are described in ORE User Guide - HTTP
> Implementation.

COMMENT: This needs further review. There should be a bag identifier. The
identifier should be a URI. The identifier should be unique. The identifier, if
it is a URI, can use any scheme (http, gsiftp, torrect, etc.). It is a good
practice to make the identifier dereferencable and accessible but it can be any
type including those that are not dereferenceable (e.g., guid:<GUID>).

In addition, *Beanbag* packages should include the following bag metadata.

    BagIt-Profile-Identifier: <URL to profile>

Where the profile conforms to the proposed profile spec [Bagit-Profile]. The
complete details for the use of the standard *BagIt* metadata are specified in
[beanbag-profile.json](beanbag-profile.json).

#### Optional metadata

    Lineage URI

The value of this attribute is the Internal-Sender-Identifier of any bags from
which the data in the current bag was derived.  This should correspond to the
lineage relationship in OAI.  TODO: Need to specify behavior of multiple
items, a list or set?

### Tag Manifest: `tagmanifest-<algorithm>.txt`

*BagIt* specifies an optional manifest file for tag files in the
`tagmanifest-<algorithm>.txt` file.

### Recommended URL-encoded Filenames

In addition to the *BagIt* requirement for UTF-8 encoding, payload file names
should also be URL-encoded per [RFC 1738].

### Recommended `text/csv` Formatting

The *Beanbag* profile recommends the use of [RFC 4180] for `text/csv` typed
payload files, also known as Comma-Separated Values (CSV) files. In addition to
RFC 4180, this profile also recommends the following.

1. The header row MUST be present with column names that exactly match the
   model described in the optional schema payload file.

2. The entire file MUST be UTF-8 encoded and each quoted or unquoted field value
   MUST be a valid UTF-8 sequence, i.e. field separator, record separator,
   quoted string delimiter, or end of file MUST NOT follow an incomplete
   multi-byte character.

### Schema Description

The "text\csv" formatted files MAY be accompanied by schema description files.
These schema files describe the structure of each "text\csv" payload file
contained in the package (or referenced by the `fetch.txt` tag file). A schema
description should only be considered *internally consistent* within the
*Beanbag* package. There are no guarantees regarding the relationship of the
schema to any external data or systems.

In the current draft of *Beanbag*, the schema may be used to describe the
structure of "text/csv" payload files. The structure includes the expected
column headers, the column header types, the relationship of columns to other
columns in the same CSV file or in other CSV files, and the relationship of
columns to other payload data files included or referenced in the package.

A non-normative example follows. Suppose the payload of a *Beanbag* package
included the following "text/csv" file and an accompanying schema file.

```
  data
   \-foo
      |- bar.csv
      \- bar-schema.json
```

The general pattern for storing CSV and schema description files is:

```
  data
   |-SCHMEA
   |  |- TABLE.csv
   |  |- TABLE-schema.json
   |  \ ...additional tables
   \- ...additional schemas
```

Where, `SCHEMA` is an optional namespace within which `TABLES` may be defined.
The `SCHEMA` is not strictly require but is RECOMMENDED.

The corresponding schema description (`TABLE-schema.json`) file could describe
it as follows. In fact, the file is really a "table definition" file that
belongs within a schema (or namespace).

```javascript
{
  "schema_name": "SCHEMA",
  "table_name": "TABLE",
  "kind": "table",
  "comment": "a human readable comment",
  "annotations": [ { "urn annotation key": "json annotation value" },... ],
  "column_definitions": [
    {
      "name": "a column name"
      "comment": "a human readable comment",
      "annotations": [ { "urn annotation key": "json annotation value" },... ],
      "type": {
        "typename": "int8 | text | timestamp | ..."
      },
      "default": "default value"
    },...
  ],
  "keys": [
    {
      "comment": "a human readable comment",
      "annotations": [ { "urn annotation key": "json annotation value" },... ],
      "unique_columns": [
        "a column name"
      ]
    }
  ],
  "foreign_keys": [
    {
      "comment": "a human readable comment",
      "foreign_key_columns": [
        {
          "schema_name": "SCHEMA",
          "table_name": "TABLE",
          "column_name": "a column name"
        }, ...
      ],
      "annotations":  { "urn annotation key": "json annotation value" },... ],
      "referenced_columns": [
        {
          "schema_name": "REFERENCED_SCHEMA",
          "table_name": "REFERENCED_TABLE",
          "column_name": "a column name"
        }, ...
      ]
    }, ...
  ]
}
```

# Notes

The *Beanbag* profile should provide recommendations for including provenance.

It has suggested that we may want to track original URL for files that are
included in the bag. This might be something like a fetched.txt which would be
in the same format as the fetch.txt file, but would also apply to files that are
currently located in the data directory.  Alternatively, this information might
be included in per-asset metadata that would be included in an OAI compliant
metadata file.

[BagIt]: https://tools.ietf.org/html/draft-kunze-bagit-11 "The BagIt File Packaging Format (V0.97)"
[BagIt-Profile]: https://github.com/ruebot/bagit-profiles
[RFC 1738]: http://www.ietf.org/rfc/rfc1738.txt "RFC 1738"
[RFC 4180]: http://www.ietf.org/rfc/rfc4180.txt "RFC 4180"
[ISO 8601]: http://www.iso.org/iso/catalogue_detail?csnumber=40874
