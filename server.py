
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="NBA 2K16 MyCareer Manager")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== DATA MODELS =====================
class Player(BaseModel):
    id: Optional[int] = None
    name: str
    overall: int
    position: str
    height: str
    weight: int

class Team(BaseModel):
    id: Optional[int] = None
    name: str
    city: str
    wins: int = 0
    losses: int = 0

class Season(BaseModel):
    id: Optional[int] = None
    year: int

class Game(BaseModel):
    id: Optional[int] = None
    home_team_id: int
    away_team_id: int
    home_score: int
    away_score: int
    date: Optional[str] = None

class MyCareerCharacter(BaseModel):
    id: Optional[int] = None
    name: str
    player_id: int
    overall: int
    xp: int = 0
    level: int = 1
    salary: int
    team_id: Optional[int] = None
    games_played: int = 0
    career_points: int = 0

class Trade(BaseModel):
    id: Optional[int] = None
    player_id: int
    from_team_id: int
    to_team_id: int
    date: Optional[str] = None

class Injury(BaseModel):
    id: Optional[int] = None
    player_id: int
    injury_type: str
    games_out: int
    date: Optional[str] = None

class Endorsement(BaseModel):
    id: Optional[int] = None
    player_id: int
    brand: str
    value: int
    date: Optional[str] = None

class Achievement(BaseModel):
    id: Optional[int] = None
    player_id: int
    name: str
    description: str
    date: Optional[str] = None

class HallOfFame(BaseModel):
    id: Optional[int] = None
    player_id: int
    name: str
    legacy_score: int
    induction_date: Optional[str] = None

# ===================== IN-MEMORY DATABASE =====================
players_db = []
teams_db = []
seasons_db = []
games_db = []
mycareer_db = []
trades_db = []
injuries_db = []
endorsements_db = []
achievements_db = []
hof_db = []

# ===================== HELPER FUNCTIONS =====================
def get_next_id(db_list):
    return max([item.get('id') for item in db_list], default=0) + 1

# ===================== PLAYERS ENDPOINTS =====================
@app.post("/players/")
async def create_player(player: Player):
    player_dict = player.dict()
    player_dict['id'] = get_next_id(players_db)
    players_db.append(player_dict)
    return player_dict

@app.get("/players/")
async def get_players():
    return players_db

@app.get("/players/{player_id}")
async def get_player(player_id: int):
    for player in players_db:
        if player['id'] == player_id:
            return player
    raise HTTPException(status_code=404, detail="Player not found")

@app.put("/players/{player_id}")
async def update_player(player_id: int, player: Player):
    for i, p in enumerate(players_db):
        if p['id'] == player_id:
            updated = player.dict()
            updated['id'] = player_id
            players_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Player not found")

@app.delete("/players/{player_id}")
async def delete_player(player_id: int):
    global players_db
    players_db = [p for p in players_db if p['id'] != player_id]
    return {"message": "Player deleted"}

# ===================== TEAMS ENDPOINTS =====================
@app.post("/teams/")
async def create_team(team: Team):
    team_dict = team.dict()
    team_dict['id'] = get_next_id(teams_db)
    teams_db.append(team_dict)
    return team_dict

@app.get("/teams/")
async def get_teams():
    return teams_db

@app.get("/teams/{team_id}")
async def get_team(team_id: int):
    for team in teams_db:
        if team['id'] == team_id:
            return team
    raise HTTPException(status_code=404, detail="Team not found")

@app.put("/teams/{team_id}")
async def update_team(team_id: int, team: Team):
    for i, t in enumerate(teams_db):
        if t['id'] == team_id:
            updated = team.dict()
            updated['id'] = team_id
            teams_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Team not found")

@app.delete("/teams/{team_id}")
async def delete_team(team_id: int):
    global teams_db
    teams_db = [t for t in teams_db if t['id'] != team_id]
    return {"message": "Team deleted"}

# ===================== SEASONS ENDPOINTS =====================
@app.post("/seasons/")
async def create_season(season: Season):
    season_dict = season.dict()
    season_dict['id'] = get_next_id(seasons_db)
    seasons_db.append(season_dict)
    return season_dict

@app.get("/seasons/")
async def get_seasons():
    return seasons_db

@app.get("/seasons/{season_id}")
async def get_season(season_id: int):
    for season in seasons_db:
        if season['id'] == season_id:
            return season
    raise HTTPException(status_code=404, detail="Season not found")

@app.delete("/seasons/{season_id}")
async def delete_season(season_id: int):
    global seasons_db
    seasons_db = [s for s in seasons_db if s['id'] != season_id]
    return {"message": "Season deleted"}

# ===================== GAMES ENDPOINTS =====================
@app.post("/games/")
async def create_game(game: Game):
    game_dict = game.dict()
    game_dict['id'] = get_next_id(games_db)
    game_dict['date'] = datetime.now().isoformat()
    
    # Update team records
    for team in teams_db:
        if team['id'] == game_dict['home_team_id']:
            if game_dict['home_score'] > game_dict['away_score']:
                team['wins'] += 1
            else:
                team['losses'] += 1
        elif team['id'] == game_dict['away_team_id']:
            if game_dict['away_score'] > game_dict['home_score']:
                team['wins'] += 1
            else:
                team['losses'] += 1
    
    games_db.append(game_dict)
    return game_dict

@app.get("/games/")
async def get_games():
    return games_db

@app.get("/games/{game_id}")
async def get_game(game_id: int):
    for game in games_db:
        if game['id'] == game_id:
            return game
    raise HTTPException(status_code=404, detail="Game not found")

@app.delete("/games/{game_id}")
async def delete_game(game_id: int):
    global games_db
    games_db = [g for g in games_db if g['id'] != game_id]
    return {"message": "Game deleted"}

# ===================== MYCAREER ENDPOINTS =====================
@app.post("/mycareer/")
async def create_mycareer(career: MyCareerCharacter):
    career_dict = career.dict()
    career_dict['id'] = get_next_id(mycareer_db)
    mycareer_db.append(career_dict)
    return career_dict

@app.get("/mycareer/")
async def get_mycareer():
    return mycareer_db

@app.get("/mycareer/{career_id}")
async def get_mycareer_character(career_id: int):
    for career in mycareer_db:
        if career['id'] == career_id:
            return career
    raise HTTPException(status_code=404, detail="Career not found")

@app.put("/mycareer/{career_id}")
async def update_mycareer(career_id: int, career: MyCareerCharacter):
    for i, c in enumerate(mycareer_db):
        if c['id'] == career_id:
            updated = career.dict()
            updated['id'] = career_id
            mycareer_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Career not found")

@app.delete("/mycareer/{career_id}")
async def delete_mycareer(career_id: int):
    global mycareer_db
    mycareer_db = [c for c in mycareer_db if c['id'] != career_id]
    return {"message": "Career deleted"}

# ===================== TRADES ENDPOINTS =====================
@app.post("/trades/")
async def create_trade(trade: Trade):
    trade_dict = trade.dict()
    trade_dict['id'] = get_next_id(trades_db)
    trade_dict['date'] = datetime.now().isoformat()
    
    # Update player's team
    for career in mycareer_db:
        if career['player_id'] == trade_dict['player_id']:
            career['team_id'] = trade_dict['to_team_id']
    
    trades_db.append(trade_dict)
    return trade_dict

@app.get("/trades/")
async def get_trades():
    return trades_db

@app.delete("/trades/{trade_id}")
async def delete_trade(trade_id: int):
    global trades_db
    trades_db = [t for t in trades_db if t['id'] != trade_id]
    return {"message": "Trade deleted"}

# ===================== INJURIES ENDPOINTS =====================
@app.post("/injuries/")
async def record_injury(injury: Injury):
    injury_dict = injury.dict()
    injury_dict['id'] = get_next_id(injuries_db)
    injury_dict['date'] = datetime.now().isoformat()
    injuries_db.append(injury_dict)
    return injury_dict

@app.get("/injuries/")
async def get_injuries():
    return injuries_db

@app.delete("/injuries/{injury_id}")
async def delete_injury(injury_id: int):
    global injuries_db
    injuries_db = [i for i in injuries_db if i['id'] != injury_id]
    return {"message": "Injury deleted"}

# ===================== ENDORSEMENTS ENDPOINTS =====================
@app.post("/endorsements/")
async def add_endorsement(endorsement: Endorsement):
    endorsement_dict = endorsement.dict()
    endorsement_dict['id'] = get_next_id(endorsements_db)
    endorsement_dict['date'] = datetime.now().isoformat()
    endorsements_db.append(endorsement_dict)
    return endorsement_dict

@app.get("/endorsements/")
async def get_endorsements():
    return endorsements_db

@app.delete("/endorsements/{endorsement_id}")
async def delete_endorsement(endorsement_id: int):
    global endorsements_db
    endorsements_db = [e for e in endorsements_db if e['id'] != endorsement_id]
    return {"message": "Endorsement deleted"}

# ===================== ACHIEVEMENTS ENDPOINTS =====================
@app.post("/achievements/")
async def unlock_achievement(achievement: Achievement):
    achievement_dict = achievement.dict()
    achievement_dict['id'] = get_next_id(achievements_db)
    achievement_dict['date'] = datetime.now().isoformat()
    achievements_db.append(achievement_dict)
    return achievement_dict

@app.get("/achievements/")
async def get_achievements():
    return achievements_db

@app.delete("/achievements/{achievement_id}")
async def delete_achievement(achievement_id: int):
    global achievements_db
    achievements_db = [a for a in achievements_db if a['id'] != achievement_id]
    return {"message": "Achievement deleted"}

# ===================== HALL OF FAME ENDPOINTS =====================
@app.post("/hall-of-fame/")
async def induct_to_hof(hof: HallOfFame):
    hof_dict = hof.dict()
    hof_dict['id'] = get_next_id(hof_db)
    hof_dict['induction_date'] = datetime.now().isoformat()
    hof_db.append(hof_dict)
    return hof_dict

@app.get("/hall-of-fame/")
async def get_hall_of_fame():
    return hof_db

@app.delete("/hall-of-fame/{hof_id}")
async def remove_from_hof(hof_id: int):
    global hof_db
    hof_db = [h for h in hof_db if h['id'] != hof_id]
    return {"message": "Hall of Fame entry removed"}

# ===================== LEADERBOARD ENDPOINTS =====================
@app.get("/leaderboard/")
async def get_leaderboard():
    sorted_careers = sorted(mycareer_db, key=lambda x: x['overall'], reverse=True)[:10]
    return sorted_careers

# ===================== STATS ENDPOINTS =====================
@app.get("/stats/")
async def get_stats():
    return {
        "total_players": len(players_db),
        "total_teams": len(teams_db),
        "total_games": len(games_db),
        "hall_of_fame_count": len(hof_db)
    }

# ===================== ROOT ENDPOINT =====================
@app.get("/")
async def root():
    return {
        "message": "NBA 2K16 MyCareer Manager API",
        "endpoints": {
            "players": "/players/",
            "teams": "/teams/",
            "seasons": "/seasons/",
            "games": "/games/",
            "mycareer": "/mycareer/",
            "trades": "/trades/",
            "injuries": "/injuries/",
            "endorsements": "/endorsements/",
            "achievements": "/achievements/",
            "hall_of_fame": "/hall-of-fame/",
            "leaderboard": "/leaderboard/",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
