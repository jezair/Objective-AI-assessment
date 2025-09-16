from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class UserCreate(BaseModel):
    username: str
    email: Optional[str]
    password: str
    role: Optional[str] = "student"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TestCreate(BaseModel):
    title: str
    description: Optional[str]


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str


class SubmissionCreate(BaseModel):
    test_id: int
    # answers: list of {question_id: int, answer: str}
    answers: List[Dict[str, Any]]


class EvalResult(BaseModel):
    question_id: int
    similarity: float
    grade: float


class SubmissionOut(BaseModel):
    id: int
    test_id: int
    student_id: int
    created_at: str
    results: Optional[List[EvalResult]]
