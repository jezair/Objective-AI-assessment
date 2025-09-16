
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from . import db, models, crud, auth, eval
from .schemas import UserCreate, Token, TestCreate, QuestionCreate, SubmissionCreate
from sqlmodel import Session
import json


app = FastAPI(title="Objective AI Assessment")


@app.on_event("startup")
def on_startup():
    db.init_db()


# Auth endpoints
@app.post('/register', response_model=Token)
def register(payload: UserCreate):
    with Session(db.engine) as session:
        existing = crud.get_user_by_username(session, payload.username)
        if existing:
            raise HTTPException(status_code=400, detail='username taken')
        hashed = auth.get_password_hash(payload.password)
        user = crud.create_user(session, payload.username, payload.email, hashed, payload.role)
        token = auth.create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}


@app.post('/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(db.engine) as session:
        user = crud.get_user_by_username(session, form_data.username)
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail='Incorrect username or password')
        token = auth.create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}


# Teacher: create test and questions
@app.post('/tests')
def create_test(payload: TestCreate, teacher = Depends(db.get_session)):
# teacher must be authenticated separately by using deps in frontend; simple demonstration here
    raise HTTPException(status_code=501, detail='Call /tests/create with auth')


from fastapi import Depends
from .deps import get_current_user, teacher_required, student_required


@app.post('/tests/create')
def create_test2(payload: TestCreate, current_user = Depends(teacher_required)):
    with Session(db.engine) as session:
        t = crud.create_test(session, payload.title, current_user.id, payload.description)
        return t


@app.post('/tests/{test_id}/questions')
def add_question(test_id: int, payload: QuestionCreate, current_user = Depends(teacher_required)):
    with Session(db.engine) as session:
        test = crud.get_test(session, test_id)

@app.get('/tests')
def list_tests():
    with Session(db.engine) as session:
        tests = session.exec(models.Test.select()).all()
        return tests

@app.get('/tests/{test_id}')
def get_test(test_id: int):
    with Session(db.engine) as session:
        t = crud.get_test(session, test_id)
        if not t:
            raise HTTPException(status_code=404, detail='Not found')
        return t

# Student: submit answers
@app.post('/submissions')
def submit(payload: SubmissionCreate, current_user = Depends(student_required)):
    with Session(db.engine) as session:
        test = crud.get_test(session, payload.test_id)
        if not test:
            raise HTTPException(status_code=404, detail='Test not found')
        # prepare lists of refs and answers in same order as questions
        questions = session.exec(models.Question.select().where(models.Question.test_id == test.id)).all()
        # map question id to index
        q_map = {q.id: q for q in questions}
        refs = []
        answers = []
        ordered_qids = []
        for item in payload.answers:
            qid = int(item.get('question_id'))
            ans = item.get('answer', '')
            if qid not in q_map:
                raise HTTPException(status_code=400, detail=f'question {qid} does not exist in test')
            refs.append(q_map[qid].reference_answer)
            answers.append(ans)
            ordered_qids.append(qid)
        sub = crud.create_submission(session, test.id, current_user.id, payload.answers)
        # run evaluation
        results = eval.evaluate_answers(refs, answers)
        # attach question_id into results
        for r, qid in zip(results, ordered_qids):
            r['question_id'] = qid
        crud.save_submission_results(session, sub.id, results)
        return {"submission_id": sub.id, "results": results}

# Teacher: view analytics for a test
@app.get('/tests/{test_id}/analytics')
def analytics(test_id: int, current_user = Depends(teacher_required)):
    with Session(db.engine) as session:
        test = crud.get_test(session, test_id)
        if not test:
            raise HTTPException(status_code=404)
        if test.teacher_id != current_user.id:
            raise HTTPException(status_code=403)
        subs = session.exec(models.Submission.select().where(models.Submission.test_id == test_id)).all()
        # collect average grade per question
        import json
        agg = {}
        counts = {}
        for s in subs:
            if not s.results:
                continue
            results = json.loads(s.results)
            for r in results:
                qid = r['question_id']
                agg[qid] = agg.get(qid, 0) + r['grade']
                counts[qid] = counts.get(qid, 0) + 1
        averages = {qid: (agg[qid] / counts[qid]) for qid in agg}
        return {"per_question_avg": averages, "submissions_count": len(subs)}