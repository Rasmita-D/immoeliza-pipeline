from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import pandas as pd
from predict import test
from typing import Literal

app = FastAPI()
'''
subtype = ['HOUSE' ,'EXCEPTIONAL_PROPERTY'
, 'FARMHOUSE' ,'APARTMENT' ,'TOWN_HOUSE',
 'VILLA', 'CASTLE', 'APARTMENT_BLOCK', 'GROUND_FLOOR' ,'CHALET' ,'PENTHOUSE',
 'MIXED_USE_BUILDING', 'COUNTRY_COTTAGE', 'BUNGALOW' ,'DUPLEX', 'MANSION',
 'FLAT_STUDIO', 'SERVICE_FLAT', 'MANOR_HOUSE', 'LOFT', 'OTHER_PROPERTY',
 'TRIPLEX', 'KOT']
class property(BaseModel):
    type_of_property: Literal['HOUSE', 'APARTMENT', 'UNKNOWN']
    subtype_of_property: Literal['HOUSE' ,'EXCEPTIONAL_PROPERTY'
, 'FARMHOUSE' ,'APARTMENT' ,'TOWN_HOUSE',
 'VILLA', 'CASTLE', 'APARTMENT_BLOCK', 'GROUND_FLOOR' ,'CHALET' ,'PENTHOUSE',
 'MIXED_USE_BUILDING', 'COUNTRY_COTTAGE', 'BUNGALOW' ,'DUPLEX', 'MANSION',
 'FLAT_STUDIO', 'SERVICE_FLAT', 'MANOR_HOUSE', 'LOFT', 'OTHER_PROPERTY',
 'TRIPLEX', 'KOT']
    number_of_rooms: int
    living_area : int 
    furnished: Optional[bool]
    open_fire: Optional[bool]
    terrace_surface: Optional[int]
    garden: Optional[int]
    swimming_pool: Optional[bool]
    facades: Optional[int]
    land_area : Optional[int]
    state_of_building: Literal['UNKNOWN','GOOD', 'TO_BE_DONE_UP', 'TO_RENOVATE' ,'AS_NEW', 'JUST_RENOVATED'
, 'TO_RESTORE']
    equipped_kitchen: Literal['UNKNOWN','HYPER_EQUIPPED', 'INSTALLED','SEMI_EQUIPPED', 'NOT_INSTALLED', 'USA_INSTALLED', 'USA_HYPER_EQUIPPED', 'USA_SEMI_EQUIPPED', 'USA_UNINSTALLED']
'''

column_names = ['Property ID', 'Locality name', 'Postal code',
       'Type of property', 'Subtype of property', 'Construction year',
       'Number of rooms', 'Surface of the plot', 'Living area', 'kitchen',
       'furnished', 'Open fire', 'Terrace', 'Garden', 'Garden orientation',
       'Number of facades', 'Swimming pool', 'State of builing',
       'Energy class', 'Primary energy consumption', 'Heating type',
       'Flood zone type', 'Double glazing', 'cadastral_income']
class property(BaseModel):
    Property_ID: int
    Locality_name : Optional[str]
    Postal_code: int
    Type_of_property : Optional[str]

    Subtype_of_property : Optional[str]
    Construction_year: int
    Number_of_rooms: int
    Surface_of_the_plot : int
    Living_area: int

    kitchen : Literal['1', 'Installed', 'Hyper equipped', 'Semi equipped',
       'Not installed']
    furnished: int
    Open_fire: int
    Terrace: int
    Garden: int

    Garden_orientation : Optional[str]
    Number_of_facades: int
    Swimming_pool:int
    State_of_builing : Literal['To renovate', 'Good', 'To be done up', 'As new', 'Just renovated',
       'nan']
    Energy_class : Optional[str]
    
    Primary_energy_consumption: int
    Heating_type: Optional[str]
    Flood_zone_type : Optional[str]
    Double_glazing : Optional[str]
    cadastral_income: int
    

@app.get('/')
def index():
    ''' Defining the starting index page'''
    return {'status':'Alive'}
@app.post('/property_info')
def create_property(data: property):
    #df = pd.DataFrame([data.dict()])
    try:
        input_data = property.model_validate(data)
    except ValidationError as e:
        return HTTPException(status_code=422, detail=f"Validation error in the request body: {str(e)}")

    data1 = input_data.model_dump()
    df = pd.DataFrame([data1])
    old_colnames = df.columns
    df = df.rename(columns=dict(zip(old_colnames, column_names)))
    try:
        output = test(df)
    except Exception as e:
        return HTTPException(status_code=500, detail='Error in prediction')
    return {'price': output}
