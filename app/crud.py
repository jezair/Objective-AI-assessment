
from sqlmodel import Session, select
from . import models
import json


def get_user_by_username(session: Session, username: str):
    return session.exec(select(models.User).where(models.User.username == username)).first()


def create_user(session: Session, username: str, email: str | None, hashed_password: str, role: str = "student"):
    user = models.User(username=username, email=email, hashed_password=hashed_password, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Tests / Questions


def create_test(session: Session, title: str, teacher_id: int, description: str | None = None):
    t = models.Test(title=title, teacher_id=teacher_id, description=description)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t


def add_question(session: Session, test_id: int, text: str, reference_answer: str):
    q = models.Question(test_id=test_id, text=text, reference_answer=reference_answer)
    session.add(q)
    session.commit()
    session.refresh(q)
    return q


def get_test(session: Session, test_id: int):
    return session.get(models.Test, test_id)


# Submissions


def create_submission(session: Session, test_id: int, student_id: int, answers: list):
    answers_json = json.dumps(answers, ensure_ascii=False)
    sub = models.Submission(test_id=test_id, student_id=student_id, answers=answers_json)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def save_submission_results(session: Session, submission_id: int, results: list):
    sub = session.get(models.Submission, submission_id)
    sub.results = json.dumps(results, ensure_ascii=False)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub