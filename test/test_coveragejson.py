# Pytests to test the coveragejson.json schema file

import pytest
from jsonschema.exceptions import ValidationError

from .test_ndArray import get_example_ndarray
from .test_tiledNdArray import get_example_tiled_ndarray
from .test_coverage import get_sample_coverage
from .test_coverageCollection import get_sample_coverage_collection
from tools.validator import runtime_validator

pytestmark = pytest.mark.schema("/schemas/coveragejson")


SAMPLE_DOMAIN = "Grid_x=1,y=1,z=0,t=0"


def test_valid_domain(validator, get_domain):
    ''' Tests an example of a domain '''

    domain = get_domain(SAMPLE_DOMAIN)
    validator.validate(domain)


def test_valid_ndarray(validator):
    ''' Tests an example of a ndarray '''

    ndarray = get_example_ndarray()
    validator.validate(ndarray)


def test_valid_tiled_ndarray(validator):
    ''' Tests an example of a tiled ndarray '''

    tiled_ndarray = get_example_tiled_ndarray()
    validator.validate(tiled_ndarray)


def test_valid_coverage(validator):
    ''' Tests an example of a coverage '''

    coverage = get_sample_coverage()
    validator.validate(coverage)


def test_valid_coverage_collection(validator):
    ''' Tests an example of a coverage collection '''

    collection = get_sample_coverage_collection()
    validator.validate(collection)


def test_missing_type(validator, get_domain):
    ''' Invalid: Grid domain with missing "type" '''

    domain = get_domain(SAMPLE_DOMAIN)
    del domain["type"]
    with pytest.raises(ValidationError):
        validator.validate(domain)


def test_misspelled_type(validator, get_domain):
    ''' Invalid: Grid domain with misspelled "type" '''

    domain = get_domain(SAMPLE_DOMAIN)
    domain["type"] = "Doman"
    with pytest.raises(ValidationError):
        validator.validate(domain)

def test_ndarray():
    ''' Valid: NdArray is valid according to custom validator '''
    ndarray=get_example_ndarray()
    runtime_validator(ndarray)
    
def test_tiledNdArray():
    ''' Valid: TiledNdArray is valid according to custom validator '''
    tiled_ndarray=get_example_tiled_ndarray()
    runtime_validator(tiled_ndarray)

def test_coverage():
    ''' Valid: Coverage is valid according to custom validator '''
    coverage=get_sample_coverage()
    runtime_validator(coverage)

def test_coverageCollection():
    ''' Valid: CoverageCollection is valid according to custom validator '''
    collection=get_sample_coverage_collection()
    runtime_validator(collection)
    
def test_invalid_document():
    ''' Invalid: Document is not valid CoverageJSON '''
    coverage=get_sample_coverage()
    coverage["type"]="NotACoverage"
    
    with pytest.raises(ValidationError):
        runtime_validator(coverage)
