from pydantic import BaseModel, Field


class Player(BaseModel):
    id: int | None = Field(
        ge=1,
    )
    first_name: str = Field(
        min_length=2, max_length=50,
        description='First name'
    )
    last_name: str = Field(
        min_length=2, max_length=50,
        description='Last name'
    )
    country: str = Field(
        min_length=2, max_length=50,
        description='Country'
    )
    age: int = Field(
        ge=15, le=45,
        description='Age'
    )

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Phil",
                "last_name": "Jones",
                "country": "England",
                "age": 35
            }
        }

class Club(BaseModel):
    id: int | None = Field(
        ge=1,
    )
    name: str = Field(
        min_length=2, max_length=50,
        description='Name'
    )
    based_in: str = Field(
        min_length=2, max_length=50,
        description='Location (city/town)'
    )
    trophies: int | None = Field(
        default=0,
        ge=0, le=999,
        description='Trophies number'
    )
    players: list[Player] | None = Field(
        max_items=36, 
        unique_items=True,
        description='Players',
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Aston Villa",
                "based_in": "Birmingham",
                "trophies": 7,
                "players": [
                    {
                        "first_name": "Wayne",
                        "last_name": "Rooney",
                        "country": "England",
                        "age": 36,
                    },
                    {
                        "first_name": "Phillipe",
                        "last_name": "Coutinho",
                        "country": "Brazil",
                        "age": 31,
                    }
                ]
            }
        }


players = [
    Player(**{
        "id": 1,
        "first_name": "Yaroslav",
        "last_name": "Rakitskyi",
        "country": "Ukraine",
        "age": 35,
    }),
    Player(**{
        "id": 2,
        "first_name": "Alex",
        "last_name": "Teisheira",
        "country": "Brazil",
        "age": 33,
    }),
    Player(**{
        "id": 3,
        "first_name": "Andrey",
        "last_name": "Yarmolneko",
        "country": "Ukraine",
        "age": 34,
    }),
]


clubs: list[Club] = [
    Club(**{
        "id": 1,
        "name": "Shakhtar",
        "based_in": "Donetsk",
        "trophies": 33,
        "players": [
            players[0],
            players[1],
        ]
    }),
    Club(**{
        "id": 2,
        "name": "Dynamo",
        "based_in": "Kyiv",
        "trophies": 34,
        "players": [
            players[2],
        ]
    })
]