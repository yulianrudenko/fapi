from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi import (
    Path, Query, Body,
    status
)
from pydantic import BaseModel, Field

from utils import generate_id


app = FastAPI()

class Club(BaseModel):
    id: int | None
    name: str = Field(
        min_length=2, max_length=50,
        description='Name'
    )
    based_in: str = Field(
        min_length=2, max_length=50,
        description='Location (city/town)'
    )
    trophies: int = Field(
        default=0, ge=0, le=999,
        description='Trophies number'
    )

clubs: list[Club] = [
    Club(**{
        "id": 1,
        "name": "Shakhtar",
        "based_in": "Donetsk",
        "trophies": 33
    }),
    Club(**{
        "id": 2,
        "name": "Dynamo",
        "based_in": "Kyiv",
        "trophies": 34
    })
]
    

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
):
    if ids:
        clubs_list = []
        for club in clubs:
            if club.id in ids:
                clubs_list.append(club)
        return {'clubs': clubs_list}
    return {'clubs': clubs[offset:limit+offset]}


@app.post('/clubs')
async def club_create(club: Club = Body(embed=True)):
    id_ = generate_id(clubs)
    club.id = id_
    clubs.append(club)
    return {'message': 'success', 'club': club}


@app.get('/clubs/{id}')
async def club_detail(
    id: int = Path(title='Club ID', description='ID of the club to retrieve')
):
    try:
        club = [club for club in clubs if club.id == id][0]
    except:
        return HTTPException(detail={'error': 'club not found'}, status_code=status.HTTP_404_NOT_FOUND)
    return {'club': club}
