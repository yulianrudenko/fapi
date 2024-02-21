from pydantic import BaseModel, Field, validator, EmailStr
from copy import deepcopy
from datetime import datetime, date


class BaseModel(BaseModel):
    @classmethod
    def from_orm(cls, obj, getter_binding=None):
        getter_binding = getter_binding or {}
        obj = deepcopy(obj)
        for field in cls.__fields__:
            method = getter_binding.get(field)
            if method is None:
                method = getattr(cls, f"get_{field}", None)
            if method is not None and callable(method):
                setattr(obj, field, method(obj))
        return super().from_orm(obj)


class Status(BaseModel):
    status: bool


class UserBase(BaseModel):
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
            raise ValueError('You must be over 18 to use this service')
        return birth_date


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserUpdate(UserBase):
    first_name: str | None = Field(
        min_length=2, max_length=110,
        description='First name',
    )
    birth_date: date | None = Field(description='Birth Date')


class UserOut(UserBase):
    id: int
    email: EmailStr
    profile_picture: str | None

    class Config:
        orm_mode = True

    @staticmethod
    def get_profile_picture(obj):
        profile_pic_name = obj.profile_picture
        if profile_pic_name is not None:
            return f'http://localhost/media/images/{obj.profile_picture}'


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
    likes_count: int

    class Config:
        orm_mode = True
