from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi import (
    Path, Query, Body,
    status
)

from models import Player, Club, players, clubs
from utils import generate_id


app = FastAPI()


''' 
---------------------------------
            CLUBS
---------------------------------
'''
@app.get('/clubs')
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
) -> set[Club]:
    if ids:
        clubs_list = []
        for club in clubs:
            if club.id in ids:
                clubs_list.append(club)
        return {'clubs': clubs_list}
    return clubs[offset:limit+offset]

print({'normal': {**Club.Config.schema_extra['example']}})
@app.post('/clubs')
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
) -> Club:
    club.id = generate_id(clubs)
    for player in club.players:
        player.id = generate_id(players)
    players.append(club.players)
    clubs.append(club)
    return club


@app.get('/clubs/{id}')
async def club_detail(
    id: int = Path(title='Club ID', description='ID of the club to retrieve')
) -> Club:
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
@app.get('/players')
async def player_list() -> set[Player]:
    return {'players': players}
