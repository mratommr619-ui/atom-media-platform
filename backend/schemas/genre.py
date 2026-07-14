from pydantic import BaseModel

class GenreBase(BaseModel):
    name: str
    slug: str

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int

    class Config:
        from_attributes = True

class CountryBase(BaseModel):
    name: str
    slug: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    id: int

    class Config:
        from_attributes = True
