# Pytests to test the ndArray.json schema file

import pytest
from jsonschema.exceptions import ValidationError
from tools.validator import validate_range

pytestmark = pytest.mark.schema("/schemas/ndArray")


def get_example_ndarray():
    return {
        "type": "NdArray",
        "dataType": "float",
        "shape": [4, 2],
        "axisNames": ["y", "x"],
        "values": [
            12.3, 12.5, 11.5, 23.1,
            None, None, 10.1, 9.1
        ]
    }


def test_valid_float_ndarray(validator):
    ''' Valid: A simple float ndarray '''

    ndarray = get_example_ndarray()
    validator.validate(ndarray)


def test_valid_integer_ndarray(validator):
    ''' Valid: A simple integer ndarray '''

    ndarray = get_example_ndarray()
    ndarray["dataType"] = "integer"
    ndarray["values"] = [
        12, 12, 11, 23,
        None, None, 10, 9
    ]
    validator.validate(ndarray)


def test_valid_string_ndarray(validator):
    ''' Valid: A simple string ndarray '''

    ndarray = get_example_ndarray()
    ndarray["dataType"] = "string"
    ndarray["values"] = [
        "a", "b", "c", "d",
        None, None, "g", "h"
    ]
    validator.validate(ndarray)


def test_compact_0d_ndarray(validator):
    ''' Valid: 0D ndarray without "shape" and "axisNames" '''

    axis = {
        "type": "NdArray",
        "dataType": "float",
        "values": [ 12.5 ]
    }
    validator.validate(axis)


def test_complete_0d_ndarray(validator):
    ''' Valid: 0D ndarray with empty "shape" and "axisNames" '''

    axis = {
        "type": "NdArray",
        "dataType": "float",
        "shape": [],
        "axisNames": [],
        "values": [ 12.5 ]
    }
    validator.validate(axis)


def test_missing_type(validator):
    ''' Invalid: NdArray with missing "type" '''

    ndarray = get_example_ndarray()
    del ndarray["type"]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_misspelled_type(validator):
    ''' Invalid: NdArray with misspelled "type" '''

    ndarray = get_example_ndarray()
    ndarray["type"] = "Ndarray"
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_missing_data_type(validator):
    ''' Invalid: NdArray with missing "dataType" '''

    ndarray = get_example_ndarray()
    del ndarray["dataType"]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_unknown_data_type(validator):
    ''' Invalid: NdArray with unknown "dataType" '''

    ndarray = get_example_ndarray()
    ndarray["dataType"] = "float64"
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_mismatching_data_type(validator):
    ''' Invalid: NdArray with "dataType" mismatching "values" '''

    ndarray = get_example_ndarray()
    ndarray["dataType"] = "string"
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_incorrect_shape_type(validator):
    ''' Invalid: NdArray with incorrect "shape" type '''

    ndarray = get_example_ndarray()
    ndarray["shape"] = [ "4", "2" ]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_incorrect_axis_names_type(validator):
    ''' Invalid: NdArray with incorrect "axisNames" type '''

    ndarray = get_example_ndarray()
    ndarray["axisNames"] = [ 0, 1 ]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_non_0d_with_missing_shape(validator):
    ''' Invalid: NdArray with missing "shape" and not 0D '''

    ndarray = get_example_ndarray()
    del ndarray["shape"]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_non_0d_with_missing_axis_names(validator):
    ''' Invalid: NdArray with missing "axisNames" and not 0D '''

    ndarray = get_example_ndarray()
    del ndarray["axisNames"]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


def test_non_0d_with_missing_shape_and_axis_names(validator):
    ''' Invalid: NdArray with missing "axisNames" & "shape" and not 0D '''

    ndarray = get_example_ndarray()
    del ndarray["shape"]
    del ndarray["axisNames"]
    with pytest.raises(ValidationError):
        validator.validate(ndarray)


# TODO test that "values" has the same length as mul("shape")
# NOTE: the spec doesn't specify this currently, which is a bug
# TODO test that "shape" and "axisNames" have the same length if non-empty

def test_valid_ndarray():
    ''' Valid: Sanity check for ndarray '''
    ndarray=get_example_ndarray()
    validate_range(ndarray)

def test_values_shape_length():
    ''' Invalid: values has same length as product(shape) '''
    ndarray=get_example_ndarray()
    ndarray["shape"]=[4,2,1]
    
    with pytest.raises(ValidationError):
        validate_range(ndarray)

def test_shape_axisNames_length():
    ''' Invalid: If non-empty, shape and axisNames have same length '''

    # TODO There are several validations that can raise an Exception before even checking for this
    ndarray=get_example_ndarray()
    ndarray["axisNames"]=["x","y","t"]
    
    with pytest.raises(ValidationError):
        validate_range(ndarray)