from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="🏏 Cricket Match API")


# Home endpoint to avoid "Not Found" at root
@app.get("/")
def home():
    return {"message": "🏏 Cricket Match API is running!", "docs": "/docs"}


# In-memory storage
matches = {}


class MatchCreate(BaseModel):
    team1: str
    team2: str
    score: int
    overs: float
    wickets: int = 0


class Match(MatchCreate):
    id: str
    win_probability: float


def predict_win(score: int, overs: float, wickets: int) -> float:
    if overs <= 0:
        return 0.5
    run_rate = score / overs
    wickets_left = 10 - wickets
    prob = 0.5
    if run_rate > 8:
        prob += 0.25
    elif run_rate < 5:
        prob -= 0.2
    if wickets_left < 3:
        prob -= 0.15
    return round(max(0.1, min(0.95, prob)), 2)


@app.post("/matches", response_model=Match, status_code=201)
def create_match(match: MatchCreate):
    match_id = str(uuid.uuid4())
    win_prob = predict_win(match.score, match.overs, match.wickets)
    new_match = {**match.dict(), "id": match_id, "win_probability": win_prob}
    matches[match_id] = new_match
    return new_match


@app.get("/matches", response_model=List[Match])
def get_all_matches():
    return list(matches.values())


@app.get("/matches/{match_id}", response_model=Match)
def get_match(match_id: str):
    if match_id not in matches:
        raise HTTPException(status_code=404, detail="Match not found")
    return matches[match_id]


@app.put("/matches/{match_id}", response_model=Match)
def update_match(match_id: str, match: MatchCreate):
    if match_id not in matches:
        raise HTTPException(status_code=404, detail="Match not found")
    win_prob = predict_win(match.score, match.overs, match.wickets)
    updated_match = {**match.dict(), "id": match_id, "win_probability": win_prob}
    matches[match_id] = updated_match
    return updated_match


@app.patch("/matches/{match_id}", response_model=Match)
def partial_update_match(
        match_id: str,
        score: Optional[int] = None,
        overs: Optional[float] = None,
        wickets: Optional[int] = None
):
    if match_id not in matches:
        raise HTTPException(status_code=404, detail="Match not found")

    current = matches[match_id]
    new_score = score if score is not None else current["score"]
    new_overs = overs if overs is not None else current["overs"]
    new_wickets = wickets if wickets is not None else current["wickets"]

    win_prob = predict_win(new_score, new_overs, new_wickets)
    matches[match_id] = {
        "team1": current["team1"],
        "team2": current["team2"],
        "score": new_score,
        "overs": new_overs,
        "wickets": new_wickets,
        "id": match_id,
        "win_probability": win_prob
    }
    return matches[match_id]


@app.delete("/matches/{match_id}", status_code=204)
def delete_match(match_id: str):
    if match_id not in matches:
        raise HTTPException(status_code=404, detail="Match not found")
    del matches[match_id]
    return