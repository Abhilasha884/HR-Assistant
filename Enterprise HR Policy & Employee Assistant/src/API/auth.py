from datetime import datetime,timedelta,timezone
from typing import Annotated
import jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from src.API.database import get_db
from src.API.db_models import Employee


SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------

password_hash = PasswordHash.recommended()


# ---------------------------------------------------------
# OAuth2
# ---------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ---------------------------------------------------------
# Password Functions
# ---------------------------------------------------------

def verify_password(plain_password: str,hashed_password: str) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(
    password: str
) -> str:

    return password_hash.hash(password)


# ---------------------------------------------------------
# Get Employee
# ---------------------------------------------------------

def get_employee(
    db: Session,
    employee_id: str
):

    return db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()


# ---------------------------------------------------------
# Authenticate Employee
# ---------------------------------------------------------

def authenticate_employee(
    db: Session,
    employee_id: str,
    password: str
):

    employee = get_employee(
        db,
        employee_id
    )

    if not employee:
        return None

    if not employee.hashed_password:
        return None

    if not verify_password(
        password,
        employee.hashed_password
    ):
        return None

    return employee


# ---------------------------------------------------------
# Create JWT Access Token
# ---------------------------------------------------------

def create_access_token(employee_id: str,expires_delta: timedelta | None = None) -> str:

    if expires_delta:

        expire = (
            datetime.now(timezone.utc)
            + expires_delta
        )

    else:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

    payload = {
        "sub": employee_id,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# ---------------------------------------------------------
# Get Current Employee
# ---------------------------------------------------------

async def get_current_employee(
    token: Annotated[
        str,
        Depends(oauth2_scheme)
    ],
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        employee_id = payload.get("sub")

        if employee_id is None:
            raise credentials_exception

    except InvalidTokenError:

        raise credentials_exception

    employee = get_employee(
        db,
        employee_id
    )

    if employee is None:

        raise credentials_exception

    if employee.employment_status != "active":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee account is not active"
        )

    return employee