from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # For login form
from typing import List, Optional
from pymongo.database import Database

from . import crud, schemas, database, auth
from .config import ACCESS_TOKEN_EXPIRE_MINUTES # For token expiry

app = FastAPI(title="OSINT Analysis API")

# --- Event Handlers for DB Connection ---
@app.on_event("startup")
async def startup_db_client():
    database.connect_to_mongo()
    # You could also initialize other resources here if needed

@app.on_event("shutdown")
async def shutdown_db_client():
    database.close_mongo_connection()

from datetime import timedelta # Import timedelta for token expiry

# --- Authentication Endpoints ---
@app.post("/users/register/", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Database = Depends(database.get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # If using email as unique identifier too (optional)
    # if user.email:
    #     db_user_email = crud.get_user_by_email(db, email=user.email) # Requires get_user_by_email in crud
    #     if db_user_email:
    #         raise HTTPException(status_code=400, detail="Email already registered")

    created_user = crud.create_user(db=db, user=user)
    # Return basic user info, not UserInDB (which has hashed_password)
    return schemas.User(
        id=str(created_user.id), # Ensure ID is string for response
        username=created_user.username,
        email=created_user.email,
        disabled=created_user.disabled
    )

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(database.get_db)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user: # user here is UserInDB from auth.authenticate_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Example of a protected endpoint
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.UserInDB = Depends(auth.get_current_active_user)):
    # current_user is UserInDB, map to User for response if needed to hide certain fields like hashed_password
    # However, schemas.User is already designed for this.
    return schemas.User(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        disabled=current_user.disabled
    )


# --- Posts Endpoints ---
@app.get("/posts/", response_model=List[schemas.Post])
async def read_posts(
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    min_risk_score: Optional[int] = None,
    language: Optional[str] = None,
    source_type: Optional[str] = None,
    group_url: Optional[str] = None, # Added for filtering
    page_url: Optional[str] = None,  # Added for filtering
    date_from: Optional[datetime] = None, # Added for filtering
    date_to: Optional[datetime] = None,   # Added for filtering
    entity_text: Optional[str] = None,    # Added for filtering
    entity_label: Optional[str] = None,   # Added for filtering
    sort_by: str = "post_time",
    sort_order: str = "desc",
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user) # Protected
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    order = -1 if sort_order.lower() == "desc" else 1

    posts = crud.get_posts_from_db(
        db, skip=skip, limit=limit, keyword=keyword,
        min_risk_score=min_risk_score, language=language,
        source_type=source_type, group_url=group_url, page_url=page_url,
        date_from=date_from, date_to=date_to,
        entity_text=entity_text, entity_label=entity_label,
        sort_by=sort_by, sort_order=order
    )
    return posts


@app.get("/posts/{post_id}", response_model=schemas.Post)
async def read_post_by_id( # Renamed for clarity
    post_id: str,
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user) # Protected
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")

    db_post = crud.get_post_by_id_from_db(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# --- Profiles Endpoints ---
@app.get("/profiles/", response_model=List[schemas.Profile])
async def read_profiles_endpoint(
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None,
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user) # Protected
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    profiles = crud.get_profiles_from_db(db, skip=skip, limit=limit, keyword=keyword)
    return profiles

@app.get("/profiles/{profile_id}", response_model=schemas.Profile)
async def read_profile_by_id(
    profile_id: str,
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user) # Protected
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    profile = crud.get_profile_by_id_from_db(db, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# --- Analytics Endpoints ---
@app.get("/analytics/risk_categories/", response_model=List[schemas.RiskCategoryCount])
async def get_risk_category_analytics(
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    return crud.get_posts_count_by_risk_category(db)

@app.get("/analytics/top_entities/", response_model=List[schemas.EntityCount])
async def get_top_entities_analytics(
    entity_label: Optional[str] = None,
    n: int = 10,
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    return crud.get_top_n_entities(db, entity_label=entity_label, n=n)

@app.get("/analytics/language_distribution/", response_model=List[schemas.LanguageCount])
async def get_language_distribution_analytics(
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    return crud.get_posts_count_by_language(db)

@app.get("/analytics/posts_time_series/", response_model=List[schemas.TimeSeriesDataPoint])
async def get_posts_time_series_analytics(
    interval: str = "day", # Query parameter: "day", "week", "month"
    db: Database = Depends(database.get_db),
    current_user: schemas.UserInDB = Depends(auth.get_current_active_user)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    if interval not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid interval. Choose from 'day', 'week', 'month'.")
    return crud.get_posts_time_series(db, interval=interval)


# --- Root Endpoint ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to the OSINT Analysis API. Visit /docs for API documentation."}

# To run the app (from the project root, assuming backend is a module):
# uvicorn backend.main:app --reload
# Or if inside backend directory:
# uvicorn main:app --reload
