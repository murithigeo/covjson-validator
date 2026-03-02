# Tests the Coverage objects that are used in the playground, as a sanity check

import os
from jsonschema import ValidationError
import pytest
import json
from tools import validator as v

pytestmark = pytest.mark.schema("/schemas/coveragejson")

def test_all_playground_coverages(validator):

    # Recursively traverse the test_data/playground directory
    rootpath = os.path.join(os.path.dirname(__file__), "test_data", "playground")
    for subdir, dirs, files in os.walk(rootpath):

        # Look only at .covjson files
        for file in (file for file in files if file.endswith(".covjson")):

            # Construct the full file path
            fullpath = os.path.join(subdir, file)

            # Load the JSON
            with open(fullpath) as f:
                j = json.load(f)

            # Validate the JSON
            validator.validate(j)
            print(fullpath)
            # TODO Over 400% test perfomance degradation
            v.runtime_validator(j)
