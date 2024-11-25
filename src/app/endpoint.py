import os
import sys
import shutil
from fastapi import APIRouter, UploadFile,File,HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse,PlainTextResponse
from pydantic import BaseModel
# from sqlalchemy.dialects.postgresql import UUID
import schemas, models,service
import uuid

from typing import List

from database import get_db

# Add the project directory to sys.path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_dir)
from core.embeddingVerctorStore import generate_embeddings,create_retrieval_chain
from core.data_processing import extract_text_from_pdf
from retrievel.llamaRetriever import query_ollama_model,query_ollama_stream
from retrievel.rag_query import query_rag_system
import logging

router=APIRouter()
current_vectorstore_dir=None
fileNames=None
dataLocation={}




# app = FastAPI()

# Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/users/", response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = models.User(user_name=user.user_name, full_name=user.full_name, password=user.password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user:schemas.UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, user)

@router.post("/login", response_model=schemas.UserLoginRespnse)
def register_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    return service.authenticate_user(db, user)

@router.get("/chat_sessions/{session_id}", response_model=schemas.ChatSessionOut)
def read_chat_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.session_id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return db_session


@router.post("/upload")
async def uploadFile(file:UploadFile=File(...)):
    try:
        global current_vectorstore_dir
        global fileNames
        upload_dir="uploads"
        vectorstores_dir=os.path.join(upload_dir,"vectorstores")
        os.makedirs(upload_dir,exist_ok=True)
        os.makedirs(vectorstores_dir,exist_ok=True)
        filePath=os.path.join(upload_dir,file.filename)
        current_vectorstore_dir=os.path.join(vectorstores_dir,file.filename.split('.')[0])
        if os.path.exists(current_vectorstore_dir):
            dataLocation[fileNames]=current_vectorstore_dir
            return JSONResponse(content={"message": "Data store already exists for this file"}, status_code=200)
        with open(filePath,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text =extract_text_from_pdf(filePath)

        documentSpliter_direcory=generate_embeddings(text,current_vectorstore_dir)
        # retrievelChain=create_retrieval_chain(documentSpliter)
        dataLocation[fileNames]=current_vectorstore_dir
        print("The dirctory___------", documentSpliter_direcory)
        return JSONResponse(content={"message": "File uploaded and processed successfully"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/Chat")
async def rag_query(query:str):
    global current_vectorstore_dir

    if current_vectorstore_dir is None:
        return JSONResponse(content={"error": "No document uploaded"}, status_code=400)
    
    try:
        retriever=create_retrieval_chain(dataLocation[fileNames])
        query_model=query_ollama_model
        rag_querys_response=query_rag_system(query_model,retriever,query)

        response = rag_querys_response, # Call the model query function

        if response:
            return {"response": response}
        else:
            raise HTTPException(status_code=500, detail="Empty response from the model")
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
class QueryPayload(BaseModel):
    query: str

@router.post("/generate_stream")
async def generate_response_stream(payload: QueryPayload):
    try:

        query = payload.query  # Extract the query from the JSON payload
        retriever = create_retrieval_chain(dataLocation[fileNames])
        rag_query_response = query_ollama_stream(retriever, fileNames,query)
        # rag_query_response = query_rag_system(query_model, retriever, query)
        return StreamingResponse(rag_query_response, media_type="text/plain")
    except Exception as error:
        logging.exception(f"Error processing the request: {str(error)}")
        return PlainTextResponse(
            content="Something went wrong, possibly a knowledge gap issue.",
            status_code=500
        )


# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import ChatSession, Message
# from app.schemas import SaveMessageRequest  # The Pydantic model created above


# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import ChatSession
# import uuid


@router.post("/chat_sessions", response_model=schemas.ChatSessionOut)
def create_chat_session(user_id: uuid.UUID, session_name: str = None, is_force:bool = False, db: Session = Depends(get_db)):
    # Create a new chat session
    if is_force:
        active_sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user_id, models.ChatSession.is_active == True ).all()

        if active_sessions:
            for session in active_sessions:
                session.is_active=False
                db.add(session)
        if active_sessions:
            db.commit()
         # Create a new session forceFully
        active_session = models.ChatSession(user_id=user_id, session_name=session_name)
        db.add(active_session)
        db.commit()
        db.refresh(active_session)
    active_session = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user_id, models.ChatSession.is_active == True ).first()   
    if not active_session:
        # Create a new session
        active_session = models.ChatSession(user_id=user_id, session_name=session_name)
        db.add(active_session)
        db.commit()
        db.refresh(active_session)

    return active_session


@router.post("/chat_sessions", response_model=schemas.ChatSessionOut)
def create_chat_session(
    user_id: uuid.UUID, 
    session_name: str = None, 
    is_force: bool = False, 
    db: Session = Depends(get_db)
):
    # Deactivate all active sessions for the user
    active_sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user_id, 
        models.ChatSession.is_active == True
    ).all()

    if active_sessions:
        for session in active_sessions:
            session.is_active = False  # Deactivate each active session
            db.add(session)  # Mark the session for update

    # Commit the deactivation changes to the database
    if active_sessions:
        db.commit()

    # Create a new session
    new_session = models.ChatSession(
        user_id=user_id, 
        session_name=session_name, 
        is_active=True
    )
    db.add(new_session)  # Add the new session
    db.commit()  # Save the changes
    db.refresh(new_session)  # Refresh to get the updated session object

    return new_session



@router.get("/session_perUser/{user_id}", response_model=List[schemas.ChatSessionOut])
def read_sessionPer_user(user_id:uuid.UUID,db:Session=Depends(get_db)):
    user_session=db.query(models.ChatSession).filter(models.ChatSession.user_id==user_id).all()
    if user_session:
        return user_session
    # raise HTTPException(status_code=409, detail="No session history for this user ")
    raise HTTPException(status_code=409, detail="No session history for this user")

@router.post("/messages", response_model=schemas.MessageOut)
def save_message(request:schemas.MessageCreate, db: Session = Depends(get_db)):
    # Validate that the chat session exists
    chat_session = db.query(models.ChatSession).filter(models.ChatSession.session_id == request.session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Validate that the sender exists (optional, depending on requirements)
    sender = db.query(models.User).filter(models.User.user_id == request.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # Create a new message
    new_message = models.Message(
        session_id=request.session_id,
        sender_id=request.sender_id,
        message_content=request.message_content,
        message_type=request.message_type,
    )

    # Save the message to the database
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message




from fastapi import Query

@router.get("/chat_sessions/{session_id}/messages", response_model=schemas.PaginatedMessageOut)
def get_chat_history(
    session_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number, starts at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Number of messages per page"),
    db: Session = Depends(get_db),
):
    # Validate that the chat session exists
    chat_session = db.query(models.ChatSession).filter(models.ChatSession.session_id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Fetch total message count for the session
    total_messages = db.query(models.Message).filter(models.Message.session_id == session_id).count()

    # Calculate offset for pagination
    offset = (page - 1) * page_size

    # Fetch paginated messages
    messages = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .order_by(models.Message.timestamp.desc())  # Order by newest first
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Return paginated response
    return {
        "session_id": session_id,
        "page": page,
        "page_size": page_size,
        "total_messages": total_messages,
        "messages": messages,
    }


# @router.post("/employee/", response_model=schemas.Employee)
# def register_employee(employee_data:schemas.Employee,db:Session=Depends(get_db)):
#     try:
#         check_employee=db.query(models.Employee).filter(models.Employee.employ_id==employee_data.employ_id).first()
#         if check_employee:
#             raise HTTPException(status_code=409, detail="Employee already registered")
#         # Add the employee (unpack the data using **)
#         add_employee = models.Employee(**employee_data.dict())
#         db.add(add_employee)
#         db.commit()
#         db.refresh(add_employee)
#         return add_employee
#     except Exception as e:
#         logging.error(f'An internal error: {e}')
#         raise HTTPException(status_code=500, detail="An internal error")
    
@router.post("/employee/", response_model=schemas.Employee)
def register_employee(employee_data: schemas.Employee, db: Session = Depends(get_db)):
    try:
        # Check if the employee already exists
        check_employee = db.query(models.Employee).filter(models.Employee.employ_id == employee_data.employ_id).first()
        if check_employee:
            raise HTTPException(status_code=409, detail="Employee already registered")

        # Create a new Employee instance using the unpacked dictionary
        new_employee = models.Employee(**employee_data.dict())
        
        # Add to the database
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)  # Refresh to get the updated instance
        
        return new_employee
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions directly
        raise http_exc
    except Exception as e:
        logging.error(f"An internal error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error")


# from fastapi import HTTPException

# @router.post("/employee/", response_model=EmployeeSchema)
# def register_employee(employee_data: EmployeeSchema, db: Session = Depends(get_db)):
#     try:
#         # Check if the employee already exists
#         check_employee = db.query(Employee).filter(Employee.employ_id == employee_data.employ_id).first()
#         if check_employee:
#             raise HTTPException(status_code=409, detail="Employee already registered")

#         # Create a new Employee instance using the unpacked dictionary
#         new_employee = Employee(**employee_data.dict())
        
#         # Add to the database
#         db.add(new_employee)
#         db.commit()
#         db.refresh(new_employee)  # Refresh to get the updated instance
        
#         return new_employee

#     except HTTPException as http_exc:
#         # Re-raise HTTP exceptions directly
#         raise http_exc
#     except Exception as e:
#         # Log and handle unexpected errors
#         logging.error(f"An internal error occurred: {e}")
#         raise HTTPException(status_code=500, detail="An internal error")




@router.get("/employee/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id:str, db:Session=Depends(get_db)):
    try:
        employee=db.query(models.Employee).filter(models.Employee.employ_id==employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="No employee found")
        return employee
    except Exception as e:
        logging.error(f"An error: {str(e)}")
        return HTTPException(status_code=500, detail="An internal error")
    
        


