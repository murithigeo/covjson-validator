# Creates a custom JSON schema validator with a reference resolver
# that can resolve any reference in the /schemas directory

import argparse
import os
import json
import jsonschema
import requests
from typing import Dict,List
from uritemplate import URITemplate
from urllib.parse import urlparse
import math
from itertools import product,permutations
from collections import defaultdict
from warnings import warn

def create_schema_store():
    ''' Creates a store that maps schema ids to schema documents '''

    # Find the directory with all the schemas in
    # TODO: find a neater way to get the file path
    schema_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../schemas')

    # Load all the schemas from this directory into the store
    schema_store = {}
    for f in os.scandir(schema_dir):
        if f.is_file() and f.path.endswith(".json"):
            abspath = os.path.abspath(f.path)
            with open(abspath) as schema_file:
                schema = json.load(schema_file)
            try:
                schema_store[schema["$id"]] = schema
            except KeyError:
                raise KeyError("$id not present in schema " + abspath)

    return schema_store


def create_custom_validator(schema_id, schema_store=None):
    ''' Creates a validator that uses the custom schema store '''

    if schema_store is None:
        schema_store = create_schema_store()
    schema = schema_store[schema_id]

    resolver = jsonschema.RefResolver(None, referrer=None, store=schema_store)
    # TODO: should be able to use validator_for(schema) to get an appropriate
    # validator, but the resulting validator doesn't seem to work
    validator = jsonschema.validators.Draft202012Validator(schema, resolver=resolver)

    return validator

validator=create_custom_validator("/schemas/coveragejson")

def custom_validator(schema:object):
    "A  validator function to validate against runtime schemas"
    return jsonschema.Draft202012Validator(schema)

def axis_name_combinations(axisData:Dict[str,int])->List[List[str],List[int]]:
    "Return all possible combinations of the expected shape and axisNames of the range\n"
    "This is required for domains where multiple axes have the same lengths and so data can be arranged in multiple valid combinations"
    
    groups=defaultdict(list)
    for axisName,length in axisData.items():
        groups[length].append(axisName)
    sortedLengths=sorted(groups.keys())
    permutations_per_length=[list(permutations(groups[l])) for l in sortedLengths]
    
    axisShape=[]
    for length in sortedLengths:
        axisShape.extend([length]*len(groups[length]))
        
    axisNames=[]
    for combo in product(*permutations_per_length):
        axisNames.append([name for sub in combo for name in sub])
    return [axisNames,axisShape]       

def loadStringDocument(url:str)->Dict:
    "Loads a URL CoverageJSON Document and validates the request and the json document"
    custom_validator({"type":"string","format":"uri"}).validate(url)
    
    res=requests.get(url)
    res.raise_for_status()
    if res.headers.get("content-type") != "application/prs.coverage+json":
        warn(f"Expected content-type header to be 'application/prs.coverage+json' but found {res.headers.get("content-type")}")
    document=res.json()
    validator.validate(document)
    return document

def validate_range(ndarr,axisNames:List[List[str]]=None,axisShape:List[int]=None,catEncodingValues:List[int]=None)->None:
    if type(ndarr) is str:
        ndarr=loadStringDocument(ndarr)
    if axisNames:
        if ndarr["axisNames"]:
            custom_validator({
                    "title":"Member 'axisNames' should match the provided arguments",
                    "description": "Given a Domain, then the value of member 'axisNames' should match that of the Domain axes",
                    "type":"array",
                    "oneOf":list(map(lambda x:{"const":x},axisNames))
                    }).validate(ndarr["axisNames"])
    if axisShape:
        if ndarr["shape"]:
            custom_validator({
                "title":"Member 'shape' should match the provided argument",
                "description":"Given the shape of the Domain, the value of member 'shape' should match the provided argument",
                "const":axisShape}).validate(ndarr["shape"])
    if ndarr["type"]=="NdArray":
        if ndarr["shape"]:
            custom_validator({
                    "title":"Product of 'shape' member should equal length of values array",
                    "description":"Inequivalence of these values indicates missing data",
                    "const":math.prod(ndarr["shape"])
                    }).validate(len(ndarr["values"]))
        if catEncodingValues:
            custom_validator({
                    "type":"array",
                    "items":{
                        "type":"integer",
                        "enum":catEncodingValues
                    }
                }).validate(ndarr["values"])
    else:
        for _,tileSet in enumerate(ndarr["tileSets"]):
            urlTemplate=URITemplate(tileSet["urlTemplate"])
            tileShape=tileSet["tileShape"]
            
            dimensions=[d for d in tileShape if d is not None]
            # Build a list for tiled axis
            tiled_axes=[
                name for name, shape_val in zip(ndarr["axisNames"],tileShape)
                if shape_val is not None
            ]
            # Create a cartesian product of available indices and for each, fetch the ndArray            
            cartesianProd=list(product(*[range(d) for d in dimensions]))

            for _,indices in enumerate(cartesianProd):
                values=dict(zip(tiled_axes, indices))
                url=urlTemplate.expand(values)
                validate_range(loadStringDocument(url),axisNames,None,catEncodingValues)
                
def validate_parameter(param)->List[int]|None:
    "Validates the categoryEncoding member"
    
    if not "categoryEncoding" in param: 
        return None
    
    if not param["observedProperty"]["category"]:
        raise jsonschema.ValidationError("observedProperty must have member 'categories' if member 'categoryEncoding' given ")
    custom_validator({
        "title":"Each CategoryEncoding must have a Category object",
        "description":"Given a categoryEncoding, then the keys of the value must have an associated Category object",
        "type":"array",
        "items":{
            "type":"string",
            "enum":list(map(lambda x: x["id"],parameter["observedProperty"]["categories"]))
                }
        }).validate(list(parameter["categoryEncoding"].keys()))
    catEncodingValues=[]
    for i in parameter["categoryEncoding"]:
        catEncoding=parameter["categoryEncoding"][i]
        if isinstance(cat,list):
            catEncodingValues+=catEncoding
        else:
            catEncodingValues.append(catEncoding)
    custom_validator({
        "title":"Uniqueness of categoryEncoding integers",
        "description":"Given a categoryEncoding, then all described values must be unique",
        "type":"array",
        "items":{
            "type":"integer",
            "uniqueItems":True
        }
    }).validate(catEncodingValues)
    
    return catEncodingValues
   
def parse_domain(dom)->[List[List[str]],List[int]]:
    "Generate expected axisNames and axis shape values"
    axisNamesAndLengths={}
    for axisName in dom["axes"]:
        axis=dom["axes"][axisName]
        if not "dataType" in axis or axis["dataType"] == "primitive":
            if not "values" in axis:
                step=(axis["stop"]-axis["start"])/(axis["num"]-1)
                values=[axis["start"]+i*step for i in range(axis["num"])]
                axis={"values":values}
                dom["axes"][axisName]=axis
            else:
                values=axis["values"]
                axisNamesAndLengths[axisName]=len(values)
                isAscending=values[0]<values[len(values)-1]
                if isAscending:
                    valid=all(x<y for x,y in zip(values,values[1:]))
                else:
                    valid=all(x>y for x,y in zip(values,values[1:]))
                custom_validator(schema={
                    "title":"Monotonicity of primitive axis",
                    "description":"Given a Primitive axis, then the values must be strictly motonotic (increasing or descreasing)",
                    "const":True
                }).validate(valid)
        axisNamesAndLengths[axisName]=len(axis["values"])
    return axis_name_combinations(axisNamesAndLengths)

def validate_coverage(cov,catEncodings:Dict[str,List[int]]=None):
    if type(cov["domain"]) is str:
        cov["domain"]=loadStringDocument(cov["domain"])
    
    if catEncodings is None:
        catEncodings={}
    if cov["parameters"]:
        for i in cov["parameters"]:
            catEncodings[i]=validate_parameter(cov["parameters"][i])
            
    custom_validator({
        "title":"Each range is described by a Parameter object",
        "description":"Each range value should have an associated parameter in the Coverage or CoverageCollection",
        "type":"array",
        "items":{
            "type":"string",
            "enum":list(catEncodings.keys())
        }}).validate(list(cov["ranges"].keys()))
    
    [axisNames,axisShape]=parse_domain(cov["domain"])
    for i in cov["ranges"]:
        validate_range(cov["ranges"][i],axisNames,axisShape,catEncodingValues=catEncodings[i])
    

def validate_coverage_collection(covcoll):
    catEncodings={}
    if obj["parameters"]:
        for i in obj["parameters"]:
            catEncodings[i]=validate_parameter(obj)
    for i in obj["coverages"]:
        validate_coverage(obj["coverages"][i],catEncodings)
  
def is_url(ref:str)->bool:
    "Simple utility to determine if string is an absolute uri"
    result= urlparse(ref)
    if not result.scheme:
        return False
    if result.scheme == "file":
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('covjson_path', type=str,
                        help='Location of CoverageJSON document. Pass an absolute URL (include scheme of link) or a relative file path. ')
    
    args = parser.parse_args()

    if is_url(args.covjson_path):
        response = requests.get(args.covjson_path)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        obj = response.json()
    else:
        # Assume the covjson_path is a local file
        with open(args.covjson_path, encoding="utf-8") as f:
            obj = json.load(f)

    validator.validate(obj)
    
    
    # Do custom validation
    match obj["type"]:
        case "NdArray":
            validate_range(obj)
        case "TiledNdArray":
            validate_range(obj)
        case "Coverage":
            validate_coverage(obj)
        case "CoverageCollection":
            validate_coverage_collection(obj)
    print("Valid!")
