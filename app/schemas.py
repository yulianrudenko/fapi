from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime, date


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(
        min_length=2, max_length=110,
        description='First name',
    )
    birth_date: date = Field(description='Birth Date')

    @validator('birth_date')
    def validate_birth_date(cls, birth_date):
        current_date = datetime.now()
        age = current_date.year - birth_date.year
        if current_date.month < birth_date.month or (current_date.month == birth_date.month and current_date.day < birth_date.day):
            age -= 1  # Subtract 1 from the age if the birthday hasn't occurred yet
        if age < 18:
            raise ValueError('you must be over 18 to create an account')
        return birth_date


class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=50)


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    type: str


class BasePost(BaseModel):
    title: str = Field(
        min_length=2, max_length=50,
        description='Post Title'
    )
    content: str = Field(
        min_length=5, max_length=1000,
        description='Post Content'
    )


class PostCreate(BasePost):
    pass


class PostUpdate(BasePost):
    title: str | None = Field(
        min_length=2, max_length=50,
        description='Post Title'
    )
    content: str | None = Field(
        min_length=5, max_length=1000,
        description='Post Content'
    )
    is_active: bool | None


class PostOut(BasePost):
    id: int | None
    user_id: int 
    published_at: datetime = Field(description='When Published')
    updated_at: datetime = Field(description='When Updated')
    is_active: bool

    class Config:
        orm_mode = True
