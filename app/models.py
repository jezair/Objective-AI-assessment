from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: Optional[str] = None
    hashed_password: str
    role: str = Field(default="student")  # 'student' or 'teacher'

    tests: List["Test"] = Relationship(back_populates="teacher")
    submissions: List["Submission"] = Relationship(back_populates="student")


class Test(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    teacher_id: int = Field(foreign_key="user.id")

    teacher: Optional[User] = Relationship(back_populates="tests")
    questions: List["Question"] = Relationship(back_populates="test")


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="test.id")
    text: str
    reference_answer: str

    test: Optional[Test] = Relationship(back_populates="questions")


class Submission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="test.id")
    student_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # We'll store answers as a JSON mapping question_id -> answer text
    answers: str  # JSON string
    # results: JSON string with similarity/grades per question
    results: Optional[str] = None

    student: Optional[User] = Relationship(back_populates="submissions")
