from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
import pandas as pd
from io import BytesIO
from .models import Base, User, Credit, Payment, Plan, Dictionary
from .database import SessionLocal, engine
from .schemas import UserResponse, PlanResponse, YearPerformanceResponse, PaymentCreate

app = FastAPI()


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def read_excel_file(file: UploadFile):
    contents = file.file.read()
    return pd.read_excel(BytesIO(contents))

@app.get("/user_credits/{user_id}", response_model=dict)
def get_user_credits(user_id: int, db: Session = Depends(get_db)):
    print(f"Requested user_id: {user_id}")

    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credits = db.query(Credit).filter(Credit.user_id == user_id).all()
    print(f"Found {len(credits)} credits for user ID: {user_id}")

    response = []
    for credit in credits:
        print(f"Credit: {credit}")
        is_closed = credit.actual_return_date is not None
        payments = db.query(Payment).filter(Payment.credit_id == credit.id).all()

        payments_body_sum = sum(payment.sum for payment in payments if payment.type_id == 1)
        payments_interest_sum = sum(payment.sum for payment in payments if payment.type_id == 2)
        payments_sum = payments_body_sum + payments_interest_sum

        overdue_days = 0
        if not is_closed and credit.return_date:
            overdue_days = (datetime.now().date() - credit.return_date).days

        response.append({
            "issuance_date": str(credit.issuance_date),
            "is_closed": is_closed,
            "return_date": str(credit.return_date) if is_closed else None,
            "body": credit.body,
            "percent": credit.percent,
            "payments_sum": payments_sum,
            "return_deadline": str(credit.return_date) if not is_closed else None,
            "overdue_days": overdue_days,
            "payments_body_sum": payments_body_sum,
            "payments_interest_sum": payments_interest_sum
        })

    
    user_info = {
        "user_id": user.id,
        "login": user.login,
        "registration_date": str(user.registration_date),
        "credits": response
    }

    print(f"Returning data: {user_info}")
    return user_info

@app.post("/import_users")
async def import_users(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = read_excel_file(file)

        required_columns = {'id', 'login', 'registration_date'}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing_columns)}")

        df.columns = df.columns.str.strip()

        for index, row in df.iterrows():
            user_id = row.get('id')
            login = row.get('login')
            registration_date = row.get('registration_date')

            if db.query(User).filter(User.id == user_id).first():
                raise HTTPException(status_code=400, detail=f"User with id {user_id} already exists.")

            try:
                registration_date = pd.to_datetime(registration_date)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid registration date format for user {login}.")

            new_user = User(id=user_id, login=login, registration_date=registration_date)
            db.add(new_user)

        db.commit()
        return {"detail": "Users successfully added."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.post("/import_plans")
async def import_plans(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = read_excel_file(file)
        df.columns = df.columns.str.strip()

        for index, row in df.iterrows():
            month = row.get('month')
            category = row.get('category')
            sum_value = row.get('sum')

            if db.query(Plan).filter(Plan.period == month, Plan.category_id == category).first():
                raise HTTPException(status_code=400, detail="Plan already exists for this month and category.")

            if isinstance(month, datetime) and month.day != 1:
                raise HTTPException(status_code=400, detail="Month must start on the first day.")

            if pd.isna(sum_value):
                raise HTTPException(status_code=400, detail="Sum cannot be empty.")

            new_plan = Plan(period=month, category_id=category, sum=sum_value)
            db.add(new_plan)

        db.commit()
        return {"detail": "Plans successfully added."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.post("/import_credits")
async def import_credits(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = read_excel_file(file)
        df.columns = df.columns.str.strip()

        for index, row in df.iterrows():
            credit_id = row.get('id')
            user_id = row.get('user_id')
            issuance_date = row.get('issuance_date')
            return_date = row.get('return_date')
            actual_return_date = row.get('actual_return_date')
            body = row.get('body')
            percent = row.get('percent')

            if db.query(Credit).filter(Credit.id == credit_id).first():
                raise HTTPException(status_code=400, detail=f"Credit with id {credit_id} already exists.")

            try:
                issuance_date = pd.to_datetime(issuance_date)
                return_date = pd.to_datetime(return_date) if pd.notna(return_date) else None
                actual_return_date = pd.to_datetime(actual_return_date) if pd.notna(actual_return_date) else None
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format.")

            new_credit = Credit(id=credit_id, user_id=user_id, issuance_date=issuance_date, return_date=return_date,
                                actual_return_date=actual_return_date, body=body, percent=percent)
            db.add(new_credit)

        db.commit()
        return {"detail": "Credits successfully added."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.post("/import_payments")
async def import_payments(payment_data: List[PaymentCreate], db: Session = Depends(get_db)):
    for payment in payment_data:
        
        credit_exists = db.query(Credit).filter(Credit.id == payment.credit_id).first()
        if not credit_exists:
            raise HTTPException(status_code=400, detail=f"Credit with id {payment.credit_id} does not exist.")

        try:
            new_payment = Payment(**payment.dict())
            db.add(new_payment)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Payment with id {payment.id} already exists.")
    return {"detail": "Payments imported successfully."}

@app.post("/import_dictionary")
async def import_dictionary(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = read_excel_file(file)
        df.columns = df.columns.str.strip()

        for index, row in df.iterrows():
            dictionary_id = row.get('id')
            name = row.get('name')

            if db.query(Dictionary).filter(Dictionary.id == dictionary_id).first():
                raise HTTPException(status_code=400, detail=f"Dictionary with id {dictionary_id} already exists.")

            new_dictionary = Dictionary(id=dictionary_id, name=name)
            db.add(new_dictionary)

        db.commit()
        return {"detail": "Dictionaries successfully added."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.get("/plans_performance")
def plans_performance(date: str, db: Session = Depends(get_db)):
    performance_data = []
    target_date = datetime.strptime(date, "%Y-%m-%d")

    plans = db.query(Plan).filter(Plan.period <= target_date).all()
    for plan in plans:
        credits_sum = db.query(Credit).filter(Credit.issuance_date >= plan.period, Credit.issuance_date <= target_date).count()
        payments_sum = db.query(Payment).filter(Payment.payment_date >= plan.period, Payment.payment_date <= target_date).count()

        performance_data.append({
            "plan": plan,
            "credits_count": credits_sum,
            "payments_count": payments_sum
        })

    return {"performance_data": performance_data}
