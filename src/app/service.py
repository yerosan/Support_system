# backend/app/auth/services.py
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import or_
import schemas, models
# from auth.tokens import create_access_token
from security import create_access_token, verify_password, get_password_hash, decode_access_token
from database import get_db
from jose import JWTError, jwt

from config import config
import logging

settings=config.settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def authenticate_user(db: Session, users:schemas.UserBase):
    try:
        user = db.query(models.User).filter(models.User.user_name == users.user_name).first()
        if not user:
            return HTTPException(status_code=200, detail={"message":"User not found", "data":None})
        if not verify_password(users.password, user.password):
            return HTTPException(status_code=200, detail={"message":"Incorrect credential", "data":None})
        return HTTPException(status_code=200, detail={"message":"Success", "data":user})
    except HTTPException as htt:
        logging.error(f"Htt Error {str(htt)}")
        raise "Something went wrong"
    except Exception as e:
        logging.error(f"Htt Error {str(e)}")
        raise "Some thing went wrong"



def create_user(db: Session, user: schemas.UserCreate):
    print("---------- The data set_____---->>>>>>>>>>>>", user)
    try:
        employee=db.query(models.Employee).filter(models.Employee.employ_id==user.employee_id).first()
        if not employee:
            raise HTTPException(status_code=200, detail={"message":"Employee Id is not found"})
       

        # Assuming `db` is your SQLAlchemy session and `models.User` is your user model
        users = db.query(models.User).filter(
            or_(
                models.User.user_name == user.user_name,
                models.User.employee_id == user.employee_id
            )
        ).first()

        if users:
            raise HTTPException(status_code=200, detail={"message":"User already exists."}) 
        hashed_password = get_password_hash(user.password)
        db_user = models.User(user_name=user.user_name,employee_id=user.employee_id, full_name=user.full_name, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return HTTPException(status_code=200, detail={"message":"Success", "data":db_user})
    except HTTPException as e:
        logging.error(f"The error,{str(e)}")
        raise e 
    except Exception as exc:
        logging.error(f"The error: {str(exc)}")
        raise exc

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data=decode_access_token(token)
    credentials_exception = HTTPException(
        status_code=200,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     user_name: str = payload.get("sub")
    #     print("The userTabels___for Datasets___===___", user_name, payload)
    #     if user_name is None:
    #         raise credentials_exception
    #     token_data = schemas.TokenData(user_name=user_name)
    # except JWTError:
    #     raise credentials_exception
    user = db.query(models.User).filter(models.User.user_name == token_data.user_name).first()
    # user = db.query(models.User).filter(models.User.username == token_data.username).first()
    print("The user is found____-----_____-------",token_data.user_name, user.user_name)
    if user is None:
        raise credentials_exception
    return user
