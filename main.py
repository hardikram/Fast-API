from fastapi import FastAPI, Path ,HTTPException, Query
import json

app = FastAPI()


def load_data():
  with open('patients.json', 'r') as f:
    data = json.load(f)
  return data


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