from datetime import date, datetime

from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.API.database import get_db
from src.API.models import EmployeeResponse,LeaveBalanceResponse,LeaveRequestResponse,PayrollResponse,HolidayResponse,LeaveRequestCreate,SessionResponse,SessionCreate,AgentRequest,AgentResponse
from src.API.db_models import Employee,LeaveBalance,LeaveRequest,Payroll,Holiday,Session
from src.agents.graph import graph
from src.app_logging.logger import get_logger

router=APIRouter()
logger=get_logger("session")

@router.get("/check")
def health_check(db:Session=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return{
        "status":"success"
    }



@router.get("/employees/{employee_id}",response_model=EmployeeResponse)
def get_employee(employee_id:str,db:Session=Depends(get_db)):
    employee=db.query(Employee).filter(Employee.employee_id==employee_id).first()
    if not employee:
        raise HTTPException(
            stsatus_code=404,
            details="Employee not found"
        )
    return employee



@router.get("/employees/{employee_id}/leave-balance",response_model=list[LeaveBalanceResponse])
def get_leave_balance(
    employee_id: str,
    db: Session = Depends(get_db)
):
    leave_balances = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id)
        .all()
    )

    if not leave_balances:
        raise HTTPException(
            status_code=404,
            detail="Leave balance not found"
        )

    return leave_balances

@router.get("/employees/{employee_id}/leave-requests",response_model=list[LeaveRequestResponse])
def get_leave_requests(
    employee_id: str,
    db: Session = Depends(get_db)
):
    leave_requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == employee_id)
        .all()
    )

    if not leave_requests:
        raise HTTPException(
            status_code=404,
            detail="Leave requests not found"
        )

    return leave_requests


@router.get("/employees/{employee_id}/payroll",response_model=PayrollResponse)
def get_payroll(employee_id:str,db:Session=Depends(get_db)):
    payroll=db.query(Payroll).filter(Payroll.employee_id==employee_id).first()
    if not payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll not found"
        )
    return payroll


@router.get("/holidays",response_model=list[HolidayResponse])
def get_holidays(db:Session=Depends(get_db)):
    holiday=db.query(Holiday).all()

    if not holiday:
        raise HTTPException(
            status_code=404,
            detail="Holiday not found"

        )
    return holiday

@router.post("/employees/{employee_id}/leave-requests")
def apply_leave(employee_id:str,leave:LeaveRequestCreate,db:Session=Depends(get_db)):
    new_leave=LeaveRequest(
        employee_id=employee_id,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        number_of_days=leave.number_of_days,
        reason=leave.reason,
        status="pending"
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave

@router.delete("/employees/{employee_id}/leave-requests/{request_id}",response_model=LeaveRequestResponse)
def cancel_leave(employee_id: str,request_id: int,db: Session = Depends(get_db)):
    
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.request_id == request_id,
        LeaveRequest.employee_id == employee_id
    ).first()

    if not leave_request:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    
    if leave_request.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Leave request is already cancelled"
        )

    
    if leave_request.status == "rejected":
        raise HTTPException(
            status_code=400,
            detail="Rejected leave request cannot be cancelled"
        )

    if leave_request.status == "approved":

        leave_balance = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type == leave_request.leave_type
        ).first()

        if not leave_balance:
            raise HTTPException(
                status_code=404,
                detail="Leave balance not found"
            )

        leave_balance.used_days -= leave_request.number_of_days

        
        if leave_balance.used_days < 0:
            leave_balance.used_days = 0

    
    leave_request.status = "cancelled"

    db.commit()
    db.refresh(leave_request)

    return leave_request

@router.put("/employees/{employee_id}/leave-requests/{request_id}",response_model=LeaveRequestResponse)
def modify_leave(employee_id: str,request_id: int,leave: LeaveRequestCreate,db: Session = Depends(get_db)):

    leave_request = (db.query(LeaveRequest).filter(
            LeaveRequest.request_id == request_id,
            LeaveRequest.employee_id == employee_id
        ).first())

    if not leave_request:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    leave_request.leave_type = leave.leave_type
    leave_request.start_date = leave.start_date
    leave_request.end_date = leave.end_date
    leave_request.number_of_days = leave.number_of_days
    leave_request.reason = leave.reason

    db.commit()
    db.refresh(leave_request)

    return leave_request


@router.put("/employees/{employee_id}/leave-requests/{request_id}/approve",response_model=LeaveRequestResponse)
def approve_leave(employee_id: str,request_id: int,db: Session = Depends(get_db)):
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.request_id == request_id,LeaveRequest.employee_id == employee_id).first()

    if not leave_request:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave requests can be approved"
        )

    leave_balance = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee_id,
        LeaveBalance.leave_type == leave_request.leave_type
    ).first()

    if not leave_balance:
        raise HTTPException(
            status_code=404,
            detail="Leave balance not found"
        )

    remaining_days = (
        leave_balance.total_days - leave_balance.used_days
    )

    if leave_request.number_of_days > remaining_days:
        raise HTTPException(
            status_code=400,
            detail="Insufficient leave balance"
        )

    leave_balance.used_days += leave_request.number_of_days

    leave_request.status = "approved"

    db.commit()
    db.refresh(leave_request)

    return leave_request


@router.get("/holidays/{year}", response_model=list[HolidayResponse])
def get_holidays_by_year(year: int,db: Session = Depends(get_db)):
    holidays = db.query(Holiday).filter(
        Holiday.holiday_year == year
    ).all()

    if not holidays:
        raise HTTPException(
            status_code=404,
            detail="No holidays found for this year"
        )

    return holidays

@router.get("/holidays/check/{holiday_date}")
def check_holiday(holiday_date: date,db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(
        Holiday.holiday_date == holiday_date
    ).first()

    if holiday:
        return {
            "is_holiday": True,
            "holiday_name": holiday.holiday_name,
            "holiday_type": holiday.holiday_type
        }

    return {
        "is_holiday": False,
        "holiday_name": None,
        "holiday_type": None
    }

@router.get("/holidays/range", response_model=list[HolidayResponse])
def get_holidays_in_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be greater than or equal to start date"
        )

    holidays = db.query(Holiday).filter(
        Holiday.holiday_date >= start_date,
        Holiday.holiday_date <= end_date
    ).order_by(Holiday.holiday_date).all()

    return holidays

@router.get("/employees/{employee_id}/payroll/latest",response_model=PayrollResponse)
def get_latest_payroll(employee_id: str,db: Session = Depends(get_db)):
    payroll = db.query(Payroll).filter(
        Payroll.employee_id == employee_id
    ).order_by(
        Payroll.pay_period.desc()
    ).first()

    if not payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll not found"
        )

    return payroll

@router.get("/employees/{employee_id}/payroll/{pay_period}",response_model=PayrollResponse)
def get_payroll_by_period(employee_id: str,pay_period: date,db: Session = Depends(get_db)):
    payroll = db.query(Payroll).filter(
        Payroll.employee_id == employee_id,
        Payroll.pay_period == pay_period
    ).first()

    if not payroll:
        raise HTTPException(
            status_code=404,
            detail="Payroll not found for this pay period"
        )

    return payroll


@router.post("/sessions",response_model=SessionResponse)
def create_session(session_data: SessionCreate,db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(
        Employee.employee_id == session_data.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    new_session = Session(employee_id=session_data.employee_id,status="active")

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    logger.info(f"LOGIN | employee_id={session_data.employee_id} "
                f"| session_id={new_session.session_id}")
    return new_session



@router.get("/sessions/{session_id}",response_model=SessionResponse)
def get_session(session_id: int,db: Session = Depends(get_db)):
    session = db.query(Session).filter(
        Session.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session

@router.put("/sessions/{session_id}/activity",response_model=SessionResponse)
def update_session_activity(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(Session).filter(
        Session.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Session is not active"
        )

    session.last_activity_at = datetime.now()

    db.commit()
    db.refresh(session)

    return session


@router.put("/sessions/{session_id}/close",response_model=SessionResponse)
def close_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(Session).filter(
        Session.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Session is already closed"
        )

    session.status = "closed"
    session.last_activity_at = datetime.now()

    db.commit()
    db.refresh(session)
    logger.info(
    f"LOGOUT | employee_id={session.employee_id} "
    f"| session_id={session.session_id}")
    return session


@router.post("/agent", response_model=AgentResponse)
async def ask_hr_agent(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    try:

        # Get the active session
        session = db.query(Session).filter(
            Session.session_id == request.session_id,
            Session.status == "active"
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Active session not found"
            )

        # Get employee ID from the session
        employee_id = session.employee_id

        # Update session activity
        session.last_activity_at = datetime.now()
        db.commit()

        # Send employee ID to LangGraph
        initial_state = {
            "messages": [
                {
                    "role": "user",
                    "content": request.user_query
                }
            ],
            "employee_id": employee_id
        }

        # Run LangGraph
        result = await graph.ainvoke(initial_state)

        # Get final response
        final_message = result["messages"][-1]

        return AgentResponse(
            response=final_message.content
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(error)}"
        )