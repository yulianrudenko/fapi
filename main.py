from fastapi import FastAPI
from fastapi.requests import Request
from pydantic import BaseModel

app = FastAPI()

class Club(BaseModel):
    name: str
    titles: int
    warnings: str | None = None

clubs: list[Club] = []

@app.get('/')
async def root():
    return {'message': 'success'}


@app.get('/clubs')
async def club_list():
    return {'clubs': clubs}


@app.post('/clubs')
async def club_create(club: Club):
    print(club)
    clubs.append(club)
    return {'message': 'success'}


@app.get('/clubs/{id}')
async def club_detail(id: int):
    return {'club': {'id': id}}


@app.patch('/clubs/{id}')
async def club_detail(id: int):
    return {'club': {'id': id}}


@app.delete('/clubs/{id}')
async def club_detail(id: int):
    return {'club': {'id': id}}
