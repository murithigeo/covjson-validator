# Pytests to test the coverage.json schema file

import pytest
from jsonschema.exceptions import ValidationError
from tools.validator import validate_coverage

pytestmark = pytest.mark.schema("/schemas/coverage")


def get_sample_coverage():
    ''' Returns a sample of a valid coverage '''

    return {
        "type" : "Coverage",
        "domain" : {
            "type" : "Domain",
            "domainType" : "Grid",
            "axes": {
                "x" : { "values": [-10, -5, 0] },
                "y" : { "values": [40, 50] },
                "z" : { "values": [5] },
                "t" : { "values": ["2010-01-01T00:12:20Z"] }
            },
            "referencing": [{
                "coordinates": ["y", "x", "z"],
                "system": {
                    "type": "GeographicCRS",
                    "id": "http://www.opengis.net/def/crs/EPSG/0/4979"
                }
            }, {
                "coordinates": ["t"],
                "system": {
                    "type": "TemporalRS",
                    "calendar": "Gregorian"
                }
            }]
        },
        "parameters" : {
            "ICEC": {
                "type" : "Parameter",
                "observedProperty" : {
                    "id" : "http://vocab.nerc.ac.uk/standard_name/sea_ice_area_fraction/",
                    "label" : {
                        "en": "Sea Ice Concentration"
                    }
                }
            }
        },
        "ranges" : {
            "ICEC" : {
                "type" : "NdArray",
                "dataType": "float",
                "axisNames": ["t", "z", "y", "x"],
                "shape": [1, 1, 2, 3],
                "values" : [ 0.5, 0.6, 0.4, 0.6, 0.2, None ]
            }
        }
    }


def test_valid_coverage(validator):
    ''' Valid: Tests an example of a coverage '''

    coverage = get_sample_coverage()
    validator.validate(coverage)


def test_domain_is_url(validator):
    ''' Valid: Coverage with "domain" as a URL '''

    coverage = get_sample_coverage()
    coverage["domain"] = "http://example.com/domain.json"
    validator.validate(coverage)


def test_range_is_url(validator):
    ''' Valid: Coverage with range as a URL '''

    coverage = get_sample_coverage()
    coverage["ranges"]["ICEC"] = "http://example.com/icec.json"
    validator.validate(coverage)


def test_range_is_tiled(validator):
    ''' Valid: Coverage with tiled range '''

    coverage = get_sample_coverage()
    coverage["ranges"]["ICEC"] = {
        "type" : "TiledNdArray",
        "dataType": "float",
        "axisNames": ["t", "z", "y", "x"],
        "shape": [1, 1, 2, 3],
        "tileSets": [{
            "tileShape": [1, None, None, None],
            "urlTemplate": "http://example.com/{t}.covjson"
        }]
    }
    validator.validate(coverage)


def test_missing_type(validator):
    ''' Invalid: Coverage with missing "type" '''

    coverage = get_sample_coverage()
    del coverage["type"]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_misspelled_type(validator):
    ''' Invalid: Coverage with misspelled "type" '''

    coverage = get_sample_coverage()
    coverage["type"] = "Coverag"
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_id_type(validator):
    ''' Invalid: Coverage with incorrect "id" type '''

    coverage = get_sample_coverage()
    coverage["id"] = 42
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_missing_domain(validator):
    ''' Invalid: Coverage with missing "domain" '''

    coverage = get_sample_coverage()
    del coverage["domain"]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_domain_type(validator):
    ''' Invalid: Coverage with incorrect "domain" type '''

    coverage = get_sample_coverage()
    coverage["domain"]["type"] = "NotADomain"
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_domain_type_type(validator):
    ''' Invalid: Coverage with incorrect "domainType" type '''

    coverage = get_sample_coverage()
    coverage["domainType"] = [ "Grid" ]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_missing_parameters(validator):
    ''' Invalid: Coverage with missing "parameters" '''

    coverage = get_sample_coverage()
    del coverage["parameters"]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_parameters_type(validator):
    ''' Invalid: Coverage with incorrect "parameters" type '''

    coverage = get_sample_coverage()
    coverage["parameters"] = list(coverage["parameters"].values())
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_parameter_groups_type(validator):
    ''' Invalid: Coverage with incorrect "parameterGroups" type '''

    coverage = get_sample_coverage()
    coverage["parameterGroups"] = coverage["parameters"]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_missing_ranges(validator):
    ''' Invalid: Coverage with missing "ranges" '''

    coverage = get_sample_coverage()
    del coverage["ranges"]
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_range_type(validator):
    ''' Invalid: Coverage with incorrect range type '''

    coverage = get_sample_coverage()
    coverage["ranges"]["ICEC"]["type"] = "SomethingElse"
    with pytest.raises(ValidationError):
        validator.validate(coverage)


def test_incorrect_alternate_ranges(validator):
    ''' Invalid: Coverage with incorrect "rangeAlternates" type '''

    coverage = get_sample_coverage()
    coverage["rangeAlternates"] = []
    with pytest.raises(ValidationError):
        validator.validate(coverage)


# TODO test that "ranges" keys match "parameters" keys
# TODO test that "shape" of (Tiled)NdArray "ranges" matches "axes" of "domain"
# TODO test that "values" of (Tiled)NdArray "ranges" matches the parameter's
#      "categoryEncoding", if existing


def test_ranges_reference_existing_param():
    ''' Invalid: All ranges in parameters reference existing parameter '''

    cov=get_sample_coverage()
    cov["ranges"]["UnlistedParam"]="http://example.com/data.covjson"
    cov["ranges"]["YetAnotherUnlistedParam"]="http://example.com/data1.covjson"
    
    with pytest.raises(ValidationError):
        validate_coverage(cov)
