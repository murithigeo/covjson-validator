# Tests the Coverage objects that are used in the playground, as a sanity check

import os
from jsonschema import ValidationError
import pytest
import json
from tools.validator import runtime_validator

pytestmark = pytest.mark.schema("/schemas/coveragejson")

def load_all_coverages():
    coverages=dict()
    
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
                coverages[file.split(".covjson")[0]]=j
    return coverages

coverages=load_all_coverages()
              
def test_all_playground_coverages(validator):
    for id in coverages:
        validator.validate(coverages[id])

def test_using_runtime_validator():
    for id in coverages:
        runtime_validator(coverages[id])