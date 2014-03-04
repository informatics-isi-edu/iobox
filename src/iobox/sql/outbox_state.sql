CREATE TABLE IF NOT EXISTS file (
    id INTEGER NOT NULL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    mtime FLOAT8,
    rtime FLOAT8,
    size INTEGER,
    checksum TEXT,
    username TEXT,
    groupname TEXT,
    must_tag BOOLEAN NOT NULL DEFAULT true
);