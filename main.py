from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi import (
    Path, Query, Body, Cookie, Header,
    status
)
from pydantic import Required
from typing import Any

from models import Player, Club, players, clubs
from utils import generate_id


app = FastAPI()


''' 
---------------------------------
            CLUBS
---------------------------------
'''
@app.get('/clubs', response_model=list[Club])
async def club_list(
    ids: list[int] | None = Query(
        default=None,
        title='Club IDs', description='List of Club IDs to retrieve',
    ),
    limit: int | None = Query(
        default=100, gte=1, le=10000,
        title='Limit', description='Limit the qty of club items',
    ),
    offset: int | None = Query(
        default=0, gte=0,
        title='Offset', description='Club index to start retrieving from',    
    ),
) -> Any:
    if ids:
        clubs_list = []
        for club in clubs:
            if club.id in ids:
                clubs_list.append(club)
    else:
        clubs_list = clubs
    return clubs_list[offset:limit+offset]


@app.post('/clubs', response_model=Club)
async def club_create(
    club: Club = Body(examples={
        'normal': {
            'summary': 'Valid',
            'description': '**Valid** payload',
            'value': {
                **Club.Config.schema_extra['example']
            }
        },
        'converted': {
            'summary': 'Converted',
            'description': '**Converted** payload',
            'value': {
                **Club.Config.schema_extra['example'],
                'trophies': '7',
            },
        },
        'invalid': {
            'summary': 'Invalid',
            'description': '`Invalid` payload',
            'value': {
                **Club.Config.schema_extra['example'],
                'trophies': 'seven',
            },
        },
    })
) -> Any:
    club.id = generate_id(clubs)
    for player in club.players:
        player.id = generate_id(players)
    players.append(club.players)
    clubs.append(club)
    return club


@app.get('/clubs/{id}', response_model=Club)
async def club_detail(
    id: int = Path(title='Club ID', description='ID of the club to retrieve')
) -> Any:
    try:
        club = [club for club in clubs if club.id == id][0]
    except:
        return HTTPException(detail={'error': 'club not found'}, status_code=status.HTTP_404_NOT_FOUND)
    return club


'''
---------------------------------
            PLAYRES
---------------------------------
'''
@app.get('/players', response_model=list[Player])
async def player_list() -> Any:
    return players
