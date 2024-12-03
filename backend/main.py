from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import json
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/medicines")
def get_all_meds():
    """
    This function reads the data.json file and returns all medicines.
    Returns:
        dict: A dictionary of all medicines
    """
    with open('data.json') as meds:
        data = json.load(meds)
    return data

@app.get("/medicines/{name}")
def get_single_med(name: str):
    """
    This function reads the data.json file and returns a single medicine by name.
    Args:
        name (str): The name of the medicine to retrieve.
    Returns:
        dict: A dictionary containing the medicine details
    """
    try:
        with open('data.json') as meds:
            data = json.load(meds)
            # Access the nested medicines array
            medicines_list = data.get("medicines", [])
            
            for med in medicines_list:
                if isinstance(med, dict) and med.get('name', '').lower() == name.lower():
                    return med
                    
        raise HTTPException(status_code=404, detail="Medicine not found")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create")
def create_med(name: str = Form(...), price: float = Form(...), description: Optional[str] = None):
    """
    This function creates a new medicine with the specified name and price.
    """
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
            medicines_list = data.get("medicines", [])
            
            # Check if medicine already exists
            if any(med.get('name', '').lower() == name.lower() for med in medicines_list):
                raise HTTPException(status_code=400, detail="Medicine already exists")
            
            new_med = {
                "name": name,
                "price": price,
                "description": description or ""
            }
            
            # Append to medicines list
            medicines_list.append(new_med)
            data["medicines"] = medicines_list
            
            # Write back to file
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            
            return new_med
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
def update_med(name: str = Form(...), price: float = Form(...)):
    """
    This function updates the price of a medicine with the specified name.
    """
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
            medicines_list = data.get("medicines", [])
            
            # Find and update medicine
            for med in medicines_list:
                if isinstance(med, dict) and med.get('name', '').lower() == name.lower():
                    med['price'] = price
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()
                    return med
                    
            raise HTTPException(status_code=404, detail="Medicine not found")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete")
def delete_med(name: str = Form(...)):
    """
    This function deletes a medicine with the specified name.
    """
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
            medicines_list = data.get("medicines", [])
            initial_length = len(medicines_list)
            
            # Filter out medicine to delete
            updated_list = [med for med in medicines_list 
                          if isinstance(med, dict) and med.get('name', '').lower() != name.lower()]
            
            if len(updated_list) == initial_length:
                raise HTTPException(status_code=404, detail="Medicine not found")
                
            # Update medicines list
            data["medicines"] = updated_list
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            
            return {"message": "Medicine deleted"}
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/average-price")
def get_average_price():
    """
    Calculate average price of all medicines
    """
    try:
        with open('data.json') as file:
            data = json.load(file)
            medicines_list = data.get("medicines", [])
            
            if not medicines_list:
                raise HTTPException(status_code=404, detail="No medicines found")
                
            # Filter out invalid prices and calculate average
            valid_prices = [med['price'] for med in medicines_list 
                          if isinstance(med, dict) and 
                          med.get('price') is not None and 
                          isinstance(med.get('price'), (int, float))]
            
            if not valid_prices:
                raise HTTPException(status_code=404, detail="No valid prices found")
                
            return {
                "average_price": statistics.mean(valid_prices),
                "total_medicines": len(valid_prices)
            }
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)