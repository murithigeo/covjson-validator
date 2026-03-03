# Pytests to test the parameter.json schema file

# TODO: could generate the "minimally valid" examples from one function, then
# modify to make them invalid in individual tests

import pytest
from jsonschema.exceptions import ValidationError
from tools.validator import validate_parameter
pytestmark = pytest.mark.schema("/schemas/parameter")


def test_valid_continuous_parameter(validator):
    ''' Tests an example of a valid continuous parameter object '''

    param = {
        "type" : "Parameter",
        "description" : { "en" : "The sea surface temperature in degrees Celsius" },
        "observedProperty" : {
            "id" : "http://vocab.nerc.ac.uk/standard_name/sea_surface_temperature/",
            "label" : { "en" : "Sea Surface Temperature" },
            "description" : {
                "en" : "The temperature of sea water near the surface"
            }
        },
        "unit" : {
            "label" : { "en": "Degree Celsius" },
            "symbol": {
                "value" : "Cel",
                "type" : "http://www.opengis.net/def/uom/UCUM/"
            }
        }
    }
    validator.validate(param)


def test_valid_categorical_parameter(validator):
    ''' Tests an example of a valid categorical parameter object '''

    param = {
        "type" : "Parameter",
        "description" : { "en" : "The land cover category" },
        "observedProperty" : {
            "id" : "http://example.com/land_cover",
            "label" : { "en" : "Land Cover" },
            "description" : { "en" : "longer description..." },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
                "description": { "en": "Very green grass." }
            }, {
                "id": "http://example.com/land_cover/categories/forest",
                "label": { "en" : "Forest" }
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [2, 3]
        }
    }
    validator.validate(param)


def test_minimal_continuous_parameter(validator):
    ''' Tests a continuous parameter object with minimal information: we'll use
        variations of this in further tests, so we want to make sure this one works '''

    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Sea Surface Temperature" },
        },
        "unit" : { "symbol": "Cel" }
    }
    validator.validate(param)


def test_minimal_categorical_parameter(validator):
    ''' Tests a categorical parameter object with minimal information: we'll use
        variations of this in further tests, so we want to make sure this one works '''

    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
            }, {
                "id": "http://example.com/land_cover/categories/forest",
                "label": { "en" : "Forest" }
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [2, 3]
        }
    }
    validator.validate(param)


def test_no_type(validator):
    ''' Invalid: parameter object with no "type" '''

    param = {
        "observedProperty" : {
            "label" : { "en" : "Sea Surface Temperature" },
        },
        "unit" : { "symbol": "Cel" }
    }
    with pytest.raises(ValidationError):
        validator.validate(param)


def test_wrong_type(validator):
    ''' Invalid: parameter object with mistyped "type" '''

    param = {
        "type" : "Paramter",
        "observedProperty" : {
            "label" : { "en" : "Sea Surface Temperature" },
        },
        "unit" : { "symbol": "Cel" }
    }
    with pytest.raises(ValidationError):
        validator.validate(param)


def test_noninteger_category_encoding(validator):
    ''' Invalid: parameter object with non-integer value in categoryEncoding '''

    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
            }, {
                "id": "http://example.com/land_cover/categories/forest",
                "label": { "en" : "Forest" }
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [2.1, 3]
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(param)


def test_nonunique_category_encoding(validator):
    ''' Invalid: parameter object with non-unique value in categoryEncoding '''

    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
            }, {
                "id": "http://example.com/land_cover/categories/forest",
                "label": { "en" : "Forest" }
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [2, 3, 3]
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(param)

def test_nonunique_category_encoding_values():
    ''' Invalid: all integers specified by the categoryEncoding must be unique '''
    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
            }, {
                "id": "http://example.com/land_cover/categories/forest",
                "label": { "en" : "Forest" }
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [1,2]
        }
    }
    
    with pytest.raises(ValidationError):
        validate_parameter(param)
        
def test_category_encoding_without_category_object():
    ''' Invalid: All categoryEncoding keys must have an associated category object in observedProperty '''
    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
            "categories": [{
                "id": "http://example.com/land_cover/categories/grass",
                "label": { "en" : "Grass" },
            }]
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [1,2]
        }
    }
    
    with pytest.raises(ValidationError):
        validate_parameter(param)

def test_category_encoding_without_categories():
    ''' Invalid: categories must be defined if categoryEncoding is present '''
    param = {
        "type" : "Parameter",
        "observedProperty" : {
            "label" : { "en" : "Land Cover" },
        },
        "categoryEncoding": {
            "http://example.com/land_cover/categories/grass": 1,
            "http://example.com/land_cover/categories/forest": [2,3]
        }
    }
    
    with pytest.raises(ValidationError):
        validate_parameter(param)
