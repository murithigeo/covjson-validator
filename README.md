# CoverageJSON Validator

This repository contains JSON Schema and associated Python code for validating [CoverageJSON](https://covjson.org) documents.

Note that this work is in active development and the validation functionality is currently limited to what can be expressed using JSON Schema. 

## Setup
 1. Install a Python environment with pip (version x or above), e.g. using conda (`conda create -n covjson-validator pip`)
 2. Install requirements (`pip install -r requirements.txt`)

N.B. Make sure to install requirements via `pip`, not `conda` (at the time of writing the version of `jsonschema` in conda was too old to run the tests).

## Running the validator

```sh
python -m tools.validator my.covjson
```

To test a server/api response, pass an absolute URL string that includes the http scheme

```sh
python -m tools.validator "https://mydomain.com/collections/cov"
```

## Testing the validator
```sh
python -m pytest
```

A more thorough (and slow) test mode can be enabled by passing `--exhaustive` to pytest. For some tests, this increases the number of parameterizations against which a test is run. This mode is also used in Continuous Integration testing via GitHub Actions.

## Downloading the JSON Schema

The latest pre-release schema is published at:
https://covjson.org/schema/dev/coveragejson.json.

The versioned schema for each CoverageJSON specification version is published at:
https://covjson.org/schema/x.y/coveragejson.json

The in-development schema generated from the latest commit to `main` is published at:
https://covjson.org/covjson-validator/schema.json

In addition, the schema is attached to each [release](https://github.com/covjson/covjson-validator/releases) on GitHub.

## Publishing the JSON Schema to covjson.org

The schema in this repository is split into multiple subschemas.
To create a bundled schema compatible with JSON Schema Draft-07, run the following commands:

```sh
python -m tools.bundle_schema --out coveragejson.json
python -m tools.downgrade_schema_to_draft07 coveragejson.json
```

For pre-release schemas, remove `$id` from the schema by running:
```sh
python -m tools.patch_schema coveragejson.json --drop-id
```

For versioned schemas, set `$id` to the target URL by running:
```sh
python -m tools.patch_schema coveragejson.json --set-id "https://covjson.org/schema/x.y/coveragejson.json"
```

After updating `$id`, create a pull request against https://github.com/covjson/covjson.github.io.
