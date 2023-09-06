from pydantic import BaseModel,  constr, ValidationError, validator
from typing import List, Dict

class UserSignupSchema(BaseModel):
    email: constr(min_length=3, regex=r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
    password1: constr(min_length=8, strict=True)
    password2: constr(min_length=8, strict=True)

    @validator('password2')
    def passwords_match(cls, value, values, **kwargs):
        if 'password1' in values and value != values['password1']:
            raise ValueError('Passwords do not match')
        return value


class UserLoginSchema(BaseModel):
    email: constr(min_length=3, regex=r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
    password: constr(min_length=8, strict=True)