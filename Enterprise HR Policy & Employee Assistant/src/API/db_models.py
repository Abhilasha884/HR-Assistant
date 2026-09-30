from sqlalchemy import Column, String, Date, DateTime, Numeric, Integer, Text
from sqlalchemy.sql import func

from src.API.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(20), primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    department = Column(String(100))
    designation = Column(String(100))
    joining_date = Column(Date, nullable=False)
    employment_status = Column(String(30), default="active")
    reporting_manager_id = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    balance_id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    leave_type = Column(String(30), nullable=False)
    total_days = Column(Numeric(5, 2), default=0)
    used_days = Column(Numeric(5, 2), default=0)
    leave_year = Column(Integer, nullable=False)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    request_id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    leave_type = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    number_of_days = Column(Numeric(5, 2), nullable=False)
    reason = Column(Text)
    status = Column(String(30), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())


class Holiday(Base):
    __tablename__ = "holidays"

    holiday_id = Column(Integer, primary_key=True)
    holiday_date = Column(Date, nullable=False, unique=True)
    holiday_name = Column(String(100), nullable=False)
    holiday_type = Column(String(100))
    holiday_year = Column(Integer, nullable=False)


class Payroll(Base):
    __tablename__ = "payroll"

    payroll_id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    pay_period = Column(Date, nullable=False)
    basic_salary = Column(Numeric(12, 2), nullable=False)
    allowances = Column(Numeric(12, 2), default=0)
    deductions = Column(Numeric(12, 2), default=0)
    net_salary = Column(Numeric(12, 2), nullable=False)


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    last_activity_at = Column(DateTime, server_default=func.now())
    status = Column(String(30), default="active")


