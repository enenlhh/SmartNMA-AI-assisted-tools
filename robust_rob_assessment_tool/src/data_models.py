from pydantic import BaseModel
from typing import List

class CoreItemAssessment(BaseModel):
    item_number: int
    step1_decision: str
    step2_decision: str
    reason: str
    quote: str

class CoreAssessmentResponse(BaseModel):
    study_id: str
    assessments: List[CoreItemAssessment]

class OptionalItemAssessment(BaseModel):
    item_number: int
    decision: str
    reason: str
    quote: str

class OptionalAssessmentResponse(BaseModel):
    study_id: str
    assessments: List[OptionalItemAssessment]
