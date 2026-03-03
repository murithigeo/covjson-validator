# Pytests to test the tiledNdArray.json schema file

import pytest
from jsonschema.exceptions import ValidationError
from tools.validator import validate_range

pytestmark = pytest.mark.schema("/schemas/tiledNdArray")


def get_example_tiled_ndarray():
    return {
        "type" : "TiledNdArray",
        "dataType": "integer",
        "axisNames": ["t", "y", "x"],
        "shape": [2, 5, 10],
        "tileSets": [{
            "tileShape": [None, None, None],
            "urlTemplate": "https://covjson.org/playground/coverages/grid-tiled/c/all.covjson"
        }, {
            "tileShape": [1, None, None],
            "urlTemplate": "https://covjson.org/playground/coverages/grid-tiled/b/{t}.covjson"
        }, {
            "tileShape": [None, 2, 3],
            "urlTemplate": "https://covjson.org/playground/coverages/grid-tiled/a/{y}-{x}.covjson"
        }]
    }


def test_valid_float_tiled_ndarray(validator):
    ''' Valid: A tiled ndarray with float data type '''

    tiled_ndarray = get_example_tiled_ndarray()
    validator.validate(tiled_ndarray)


def test_valid_integer_ndarray(validator):
    ''' Valid: A simple integer ndarray '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["dataType"] = "integer"
    validator.validate(tiled_ndarray)


def test_valid_string_ndarray(validator):
    ''' Valid: A simple string ndarray '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["dataType"] = "string"
    validator.validate(tiled_ndarray)


def test_missing_type(validator):
    ''' Invalid: Tiled ndarray with missing "type" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["type"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_misspelled_type(validator):
    ''' Invalid: Tiled ndarray with misspelled "type" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["type"] = "TiledNdarray"
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_data_type(validator):
    ''' Invalid: Tiled ndarray with missing "dataType" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["dataType"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_unknown_data_type(validator):
    ''' Invalid: Tiled ndarray with unknown "dataType" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["dataType"] = "float64"
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_incorrect_shape_type(validator):
    ''' Invalid: Tiled ndarray with incorrect "shape" type '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["shape"] = [ "4", "2" ]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_shape(validator):
    ''' Invalid: Tiled ndarray with missing "shape" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["shape"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_empty_shape(validator):
    ''' Invalid: Tiled ndarray with empty "shape" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["shape"] = [ ]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_incorrect_axis_names_type(validator):
    ''' Invalid: Tiled ndarray with incorrect "axisNames" type '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["axisNames"] = [ 0, 1 ]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_axis_names(validator):
    ''' Invalid: Tiled ndarray with missing "axisNames" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["axisNames"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_empty_axis_names(validator):
    ''' Invalid: Tiled ndarray with empty "axisNames" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["axisNames"] = []
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_empty_tilesets(validator):
    ''' Invalid: Tiled ndarray with empty "tileSets" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["tileSets"] = []
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_tilesets(validator):
    ''' Invalid: Tiled ndarray with missing "tileSets" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["tileSets"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_incorrect_tileset_type(validator):
    ''' Invalid: Tiled ndarray with incorrect "tileSets" item type '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["tileSets"] = [ "http://example.com/c/{y}-{x}.covjson" ]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_tile_shape(validator):
    ''' Invalid: Tiled ndarray with missing "tileShape" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["tileSets"][0]["tileShape"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_empty_tile_shape(validator):
    ''' Invalid: Tiled ndarray with empty "tileShape" '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["tileSets"][0]["tileShape"] = []
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_incorrect_tile_shape_type(validator):
    ''' Invalid: Tiled ndarray with incorrect "tileShape" type '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["tileSets"][0]["tileShape"] = 10
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_missing_url_template(validator):
    ''' Invalid: Tiled ndarray with missing "urlTemplate" '''

    tiled_ndarray = get_example_tiled_ndarray()
    del tiled_ndarray["tileSets"][0]["urlTemplate"]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


def test_incorrect_url_template_type(validator):
    ''' Invalid: Tiled ndarray with incorrect "urlTemplate" type '''

    tiled_ndarray = get_example_tiled_ndarray()
    tiled_ndarray["tileSets"][0]["urlTemplate"] = \
        [ tiled_ndarray["tileSets"][0]["urlTemplate"] ]
    with pytest.raises(ValidationError):
        validator.validate(tiled_ndarray)


# TODO test that "urlTemplate" is a valid RFC 6570 Level 1 URI template

def test_axisnames_shape_length_valid():
    ''' Valid: shape and axisNames have same length '''
    tiled_ndarray=get_example_tiled_ndarray()
    validate_range(tiled_ndarray)
    
def test_axisnames_shape_length():
    ''' Invalid: shape and axisNames have the same length '''
    tiled_ndarray=get_example_tiled_ndarray()
    tiled_ndarray["axisNames"]=tiled_ndarray["axisNames"][0:len(tiled_ndarray["axisNames"])-2]
    
    with pytest.raises(ValidationError):
        validate_range(tiled_ndarray)

def tile_shape_shape_length():
    ''' Invalid: tileShape and shape have same length '''
    
    tiled_ndarray=get_example_tiled_ndarray()
    tiled_ndarray["shape"]=tiled_ndarray["shape"][0:len(tiled_ndarray["shape"])-2]
    
    with pytest.raises(ValidationError):
        validate_range(tiled_ndarray)
        
def urltemplate_contains_right_variables():
    ''' Invalid: Validate that each urlTemplate only contains axisName variables '''
    
    tiled_ndarray=get_example_tiled_ndarray()
    tiled_ndarray["tileSets"]=[{"urlTemplate":"https://covjson.org/playground/coverages/grid-tiled/c/{x}/all.covjson"}]
    
    with pytest.raises(ValidationError):
        validate_range(tiled_ndarray)