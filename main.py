from fastapi import FastAPI, Path ,HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
  id: Annotated[str, Field(...,description='ID of the patient',examples=['P001'])]
  name: Annotated[str, Field(..., description='Name of the patient')]
  city: Annotated[str, Field(..., description='City where the patient is living')]
  age: Annotated[int, Field(..., gt=0, le=120, description='Age of the patient')]
  gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
  height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
  weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

  @computed_field
  @property
  def bmi(self) -> float:
    bmi = round(self.weight/(self.height**2),2)
    return bmi

  @computed_field
  @property
  def verdict(self) -> str:
    if self.bmi < 18.5:
      return "Underweight"
    elif 18.5 <= self.bmi < 24.9:
      return "Normal weight"
    elif 25 <= self.bmi < 29.9:
      return "Overweight"
    else:
      return "Obesity"
    
class PatientUpdate(BaseModel):
  name: Annotated[Optional[str], Field(default=None)]
  city: Annotated[Optional[str], Field(default=None)]
  age: Annotated[Optional[int], Field(gt=0, le=120, default=None)]
  gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
  height: Annotated[Optional[float], Field(gt=0, default=None)]
  weight: Annotated[Optional[float], Field(gt=0, default=None)]


def load_data():
  with open('patients.json', "r") as f:
    data = json.load(f)
  return data

def save_data(data):
  with open('patients.json', "w") as f:
    json.dump(data, f)


@app.get('/')
def hello():
  return {"message": "Hello World"}

@app.get('/about')
def about():
  return {"message": "About page"}

@app.get('/view')
def view():
  data = load_data()
  return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if patient_id in data:
      return data[patient_id]
    
    raise HTTPException(status_code=404, detail="Patient not found.")

@app.get('/sort')
def sort_patient(sort_by: str = Query(..., description = "Short on the basis of height, weight or bmi"), order: str =  Query('asc', description = 'sort in asc or desc order')):
  valid_fields = ['height', 'weight', 'bmi']
  if sort_by not in valid_fields:
    raise HTTPException(status_code=400, detail=f"Invalid field select from {valid_fields}")
  
  if order not in ['asc', 'desc']:
    raise HTTPException(status_code=400, detail="Invalid order select between asc and desc")
  
  data = load_data()

  sorted_data =  sorted(data.values(), key= lambda x: x[sort_by], reverse= True if order == 'desc' else False)
  return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
  data = load_data()
  if patient.id in data:
    raise HTTPException(status_code=400, detail="Patient with this ID already exists.")
  
  data[patient.id] = patient.model_dump(exclude=['id'])
  
  save_data(data)
  
  return JSONResponse(status_code=201, content={"message": "Patient created successfully."})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
  data = load_data()

  if patient_id not in data:
    raise HTTPException(status_code=404, detail="Patient not Found")
  
  existing_patient_info = data[patient_id]

  update_patient_info = patient_update.model_dump(exclude_unset=True)

  for key, value in update_patient_info.items():
    existing_patient_info[key] = value
  
  existing_patient_info['id'] = patient_id
  patient_pydantic_obj = Patient(**existing_patient_info)

  existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')


  data[patient_id] = existing_patient_info
    
  save_data(data)

  return JSONResponse(content={'message': "Patient Updated"}, status_code=200)


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
  
  data = load_data()

  if patient_id not in data:
    raise HTTPException(status_code=404, detail="Patient not found")
  
  del data[patient_id]
  
  save_data(data)

  return JSONResponse(content={"message": "Patient deleted"})