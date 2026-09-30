from pydantic import BaseModel,EmailStr,Field,computed_field
from sqlalchemy import Column, String, Date, DateTime, Float
from datetime import date,datetime
from typing import Optional
from src.API.database import Base
from sqlalchemy.sql import func


class EmployeeBase(BaseModel):
    full_name: str
    email: EmailStr
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: date
    employment_status: str = "active"
    reporting_manager_id: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    employee_id:str

class EmployeeResponse(EmployeeBase):
    employee_id:str
    created_at:datetime
    updated_at:datetime

class LeaveBalanceBase(BaseModel):
    employee_id:str
    leave_type:str
    total_days:float=Field(default=0,ge=0)
    used_days:float=Field(default=0,ge=0)
    leave_year:int

class LeaveBalanceCreate(LeaveBalanceBase):
    pass

class LeaveBalanceResponse(LeaveBalanceBase):
    balance_id: int

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def remaining_days(self) -> float:
        return self.total_days - self.used_days


class LeaveRequestBase(BaseModel):
    employee_id:str
    leave_type:str
    start_date:date
    end_date:date
    number_of_days:float=Field(gt=0)
    reason:Optional[str]=None

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestResponse(LeaveRequestBase):
    request_id:int
    status:str
    created_at:datetime
    updated_at:datetime
    model_config = {"from_attributes": True}

class HolidayBase(BaseModel):
    holiday_date:date
    holiday_name:str
    holiday_type:Optional[str]=None
    holiday_year:int

class HolidayCreate(HolidayBase):
    pass

class HolidayResponse(HolidayBase):
    holiday_id:int

class PayrollBase(BaseModel):
    employee_id: str
    pay_period: date
    basic_salary: float = Field(ge=0)
    allowances: float = Field(default=0, ge=0)
    deductions: float = Field(default=0, ge=0)
    net_salary: float = Field(ge=0)


class PayrollCreate(PayrollBase):
    pass


class PayrollResponse(PayrollBase):
    payroll_id: int



class SessionCreate(BaseModel):
    employee_id: str


class SessionResponse(BaseModel):
    session_id: int
    employee_id: str
    started_at: datetime
    last_activity_at: datetime
    status: str

    model_config = {"from_attributes": True}


class AgentRequest(BaseModel):
    session_id: int
    user_query: str


class AgentResponse(BaseModel):
    response: str


class SessionRequest(BaseModel):
    employee_id:str

class SessionResponse(BaseModel):
    session_id:int
    employee_id:str
    