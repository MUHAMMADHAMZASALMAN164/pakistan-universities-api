from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="🎓 Pakistan Universities API")

@app.get("/")
def home():
    return {"message": "🎓 Pakistan Universities API is running!", "docs": "/docs"}

unis = {}
next_id = 1

class UniCreate(BaseModel):
    name: str
    city: str
    province: str
    established: int
    ranking_national: int

class Uni(UniCreate):
    id: int

@app.post("/universities", response_model=Uni, status_code=201)
def add_university(uni: UniCreate):
    global next_id
    new_uni = {**uni.dict(), "id": next_id}
    unis[next_id] = new_uni
    next_id += 1
    return new_uni

@app.get("/universities", response_model=List[Uni])
def list_universities():
    return list(unis.values())

@app.get("/universities/{uni_id}", response_model=Uni)
def get_university(uni_id: int):
    if uni_id not in unis:
        raise HTTPException(status_code=404, detail="University not found")
    return unis[uni_id]

@app.put("/universities/{uni_id}", response_model=Uni)
def update_university(uni_id: int, uni: UniCreate):
    if uni_id not in unis:
        raise HTTPException(status_code=404, detail="University not found")
    unis[uni_id] = {**uni.dict(), "id": uni_id}
    return unis[uni_id]

@app.patch("/universities/{uni_id}", response_model=Uni)
def partial_update_university(
    uni_id: int,
    ranking_national: Optional[int] = None,
    city: Optional[str] = None
):
    if uni_id not in unis:
        raise HTTPException(status_code=404, detail="University not found")
    if ranking_national is not None:
        unis[uni_id]["ranking_national"] = ranking_national
    if city is not None:
        unis[uni_id]["city"] = city
    return unis[uni_id]

@app.delete("/universities/{uni_id}", status_code=204)
def delete_university(uni_id: int):
    if uni_id not in unis:
        raise HTTPException(status_code=404, detail="University not found")
    del unis[uni_id]
    return