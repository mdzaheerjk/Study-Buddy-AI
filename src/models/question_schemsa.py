from typing import List
from pydantic import BaseModel,Field,validator

class MCQQuestion(BaseModel):
    question:str =Field(description='The Question Text')

    options:List[str] =Field(description='List of 4 options')

    correct_answer:str = Field(description='The Correct answer from the options')

    @validator('question',pre=True)
    def clean_question(cls,v):
        if isinstance(v,dict):
            return v.get('description',str(v))
        return str(v)


class FillBlankQuestion(BaseModel):
    question:str=Field(description="The Question text with '__'  for the blank")

    answer:str =Field(description='The Correct word or phrase for the Blank')

    @validator('question',pre=True)
    def clean_question(cls,v):
        if isinstance(v,dict):
            return v.get('description',str(v))
        return str(v)