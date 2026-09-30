from datetime import date, datetime

from src.API.database import session
from src.API.db_models import Employee,LeaveBalance,Holiday,LeaveRequest,Payroll,Session

def get_employee_details(employee_id: str) -> dict:
    """
    Get employee details using employee ID.
    """

    db = session()

    try:
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )

        if not employee:
            return {
                "error": "Employee not found",
                "employee_id": employee_id
            }

        return {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "email": employee.email,
            "department": employee.department,
            "designation": employee.designation,
            "joining_date": employee.joining_date.isoformat(),
            "employment_status": employee.employment_status,
            "reporting_manager_id": employee.reporting_manager_id
        }

    finally:
        db.close()


def get_leave_balance(employee_id:str)->dict:
    """
    Get leave balance for an employee.
    """
    db=session()
    try:
        balances=db.query(LeaveBalance).filter(LeaveBalance.employee_id==employee_id).all()
        if not balances:
                return[
                    {
                        "error":"Leave balance not found",
                        "employee_id":employee_id
                    }
                ]
        
        return {
            "employee_id": employee_id,
            "leave_balances": [
                {
                    "leave_type": balance.leave_type,
                    "total_days": float(balance.total_days),
                    "used_days": float(balance.used_days),
                    "remaining_days": float(
                        balance.total_days - balance.used_days
                    ),
                    "leave_year": balance.leave_year
                }
                for balance in balances
            ]
        }
    finally:
         db.close()
    


def get_leave_requests(employee_id: str) -> dict:
    """
    Get all leave requests for an employee.
    """

    db = session()

    try:
        requests = (
            db.query(LeaveRequest)
            .filter(LeaveRequest.employee_id == employee_id)
            .all()
        )

        if not requests:
            return {
                "employee_id": employee_id,
                "leave_requests": []
            }

        return {
            "employee_id": employee_id,
            "leave_requests": [
                {
                    "request_id": request.request_id,
                    "leave_type": request.leave_type,
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                    "number_of_days": float(request.number_of_days),
                    "reason": request.reason,
                    "status": request.status,
                    "created_at": request.created_at.isoformat()
                    if request.created_at else None
                }
                for request in requests
            ]
        }

    finally:
        db.close()



def get_holidays(year: int) -> dict:
    """
    Get company holidays for a given year.
    """

    db = session()

    try:
        holidays = (
            db.query(Holiday)
            .filter(Holiday.holiday_year == year)
            .order_by(Holiday.holiday_date)
            .all()
        )

        return {
            "year": year,
            "holidays": [
                {
                    "holiday_id": holiday.holiday_id,
                    "holiday_date": holiday.holiday_date.isoformat(),
                    "holiday_name": holiday.holiday_name,
                    "holiday_type": holiday.holiday_type
                }
                for holiday in holidays
            ]
        }

    finally:
        db.close()


def check_holiday(holiday_date: str) -> dict:
    """
    Check whether a given date is a company holiday.
    """

    db = session()

    try:
        check_date = date.fromisoformat(holiday_date)

        holiday = (
            db.query(Holiday)
            .filter(Holiday.holiday_date == check_date)
            .first()
        )

        if not holiday:
            return {
                "date": holiday_date,
                "is_holiday": False,
                "holiday_name": None,
                "holiday_type": None
            }

        return {
            "date": holiday.holiday_date.isoformat(),
            "is_holiday": True,
            "holiday_name": holiday.holiday_name,
            "holiday_type": holiday.holiday_type
        }

    finally:
        db.close()

def get_payroll(employee_id:str)->dict:
    """Get payroll details of employee from employee ID"""
    try:
        db=session()
        payroll_records=db.query(Payroll).filter(Payroll.employee_id==employee_id).order_by(Payroll.pay_period.desc()).all()
        if not payroll_records:
                return{
                    "employee_id":employee_id,
                    "payroll_records":[]
                }
        return {
                    "employee_id": employee_id,
                    "payroll_records": [
                        {
                            "payroll_id": payroll.payroll_id,
                            "pay_period": payroll.pay_period.isoformat(),
                            "basic_salary": float(payroll.basic_salary),
                            "allowances": float(payroll.allowances),
                            "deductions": float(payroll.deductions),
                            "net_salary": float(payroll.net_salary)
                        }
                        for payroll in payroll_records
                    ]
            }
    finally:
        db.close()


def get_latest_payroll(employee_id: str) -> dict:
    """
    Get the latest payroll record for an employee.
    """
    db = session()
    try:
        payroll = (
            db.query(Payroll)
            .filter(Payroll.employee_id == employee_id)
            .order_by(Payroll.pay_period.desc())
            .first()
        )

        if not payroll:
            return {
                "error": "Payroll information not found",
                "employee_id": employee_id
            }

        return {
            "employee_id": payroll.employee_id,
            "payroll_id": payroll.payroll_id,
            "pay_period": payroll.pay_period.isoformat(),
            "basic_salary": float(payroll.basic_salary),
            "allowances": float(payroll.allowances),
            "deductions": float(payroll.deductions),
            "net_salary": float(payroll.net_salary)
        }

    finally:
        db.close()


def create_session(employee_id: str) -> dict:
    """
    Create a new session for an employee.
    """

    db = session()

    try:
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )

        if not employee:
            return {
                "error": "Employee not found",
                "employee_id": employee_id
            }

        new_session = Session(
            employee_id=employee_id,
            status="active"
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return {
            "session_id": new_session.session_id,
            "employee_id": new_session.employee_id,
            "started_at": new_session.started_at.isoformat(),
            "last_activity_at": new_session.last_activity_at.isoformat(),
            "status": new_session.status
        }

    finally:
        db.close()


def get_session(session_id: int) -> dict:
    """
    Get session details using session ID.
    """

    db = session()

    try:
        current_session = (
            db.query(Session)
            .filter(Session.session_id == session_id)
            .first()
        )

        if not current_session:
            return {
                "error": "Session not found",
                "session_id": session_id
            }

        return {
            "session_id": current_session.session_id,
            "employee_id": current_session.employee_id,
            "started_at": current_session.started_at.isoformat(),
            "last_activity_at": current_session.last_activity_at.isoformat(),
            "status": current_session.status
        }

    finally:
        db.close()

def update_session_activity(session_id: int) -> dict:
    """
    Update the last activity time of a session.
    """

    db = session()

    try:
        current_session = (
            db.query(Session)
            .filter(Session.session_id == session_id)
            .first()
        )

        if not current_session:
            return {
                "error": "Session not found",
                "session_id": session_id
            }

        current_session.last_activity_at = datetime.now()

        db.commit()
        db.refresh(current_session)

        return {
            "session_id": current_session.session_id,
            "employee_id": current_session.employee_id,
            "last_activity_at": current_session.last_activity_at.isoformat(),
            "status": current_session.status
        }

    finally:
        db.close()


def close_session(session_id: int) -> dict:
    """
    Close an active employee session.
    """

    db = session()

    try:
        current_session = (
            db.query(Session)
            .filter(Session.session_id == session_id)
            .first()
        )

        if not current_session:
            return {
                "error": "Session not found",
                "session_id": session_id
            }

        if current_session.status == "closed":
            return {
                "error": "Session already closed",
                "session_id": session_id
            }

        current_session.status = "closed"
        current_session.last_activity_at = datetime.now()

        db.commit()
        db.refresh(current_session)

        return {
            "session_id": current_session.session_id,
            "employee_id": current_session.employee_id,
            "last_activity_at": current_session.last_activity_at.isoformat(),
            "status": current_session.status
        }

    finally:
        db.close()

def submit_leave_requests(employee_id:str,leave_type:str,start_date:str,end_date:str,number_of_days:float,reason:str=None)->dict:
    """Submit new leave for employee"""
    db=session()
    try:
        employee=(db.query(Employee).filter(Employee.employee_id==employee_id).first())
        if not employee:
            return{
                "error":"Employee not found",
                "employee_id":employee_id
            }
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        if end < start:
            return {
                "error": "End date cannot be before start date"
            }
        new_request = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start,
            end_date=end,
            number_of_days=number_of_days,
            reason=reason,
            status="pending"
        )

        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return {
            "message": "Leave request submitted successfully",
            "request_id": new_request.request_id,
            "employee_id": new_request.employee_id,
            "leave_type": new_request.leave_type,
            "start_date": new_request.start_date.isoformat(),
            "end_date": new_request.end_date.isoformat(),
            "number_of_days": float(new_request.number_of_days),
            "reason": new_request.reason,
            "status": new_request.status
        }

    except Exception as e:
        db.rollback()

        return {
            "error": "Failed to submit leave request",
            "details": str(e)
        }

    finally:
        db.close()

def cancel_leave_request(employee_id: str,request_id: int) -> dict:
    """
    Cancel an employee's leave request.
    """

    db = session()

    try:
        leave_request = (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.request_id == request_id,
                LeaveRequest.employee_id == employee_id
            )
            .first()
        )

        if not leave_request:
            return {
                "error": "Leave request not found",
                "request_id": request_id,
                "employee_id": employee_id
            }

        if leave_request.status == "cancelled":
            return {
                "error": "Leave request is already cancelled",
                "request_id": request_id
            }

        if leave_request.status == "rejected":
            return {
                "error": "Rejected leave request cannot be cancelled",
                "request_id": request_id
            }

    
        if leave_request.status == "approved":

            leave_balance = (
                db.query(LeaveBalance)
                .filter(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type == leave_request.leave_type
                )
                .first()
            )

            if leave_balance:
                leave_balance.used_days -= leave_request.number_of_days

        leave_request.status = "cancelled"
        leave_request.updated_at = datetime.now()

        db.commit()
        db.refresh(leave_request)

        return {
            "message": "Leave request cancelled successfully",
            "request_id": leave_request.request_id,
            "employee_id": leave_request.employee_id,
            "leave_type": leave_request.leave_type,
            "status": leave_request.status
        }

    except Exception as e:
        db.rollback()

        return {
            "error": "Failed to cancel leave request",
            "details": str(e)
        }

    finally:
        db.close()


def approve_leave_request(
    employee_id: str,
    request_id: int
) -> dict:
    """
    Approve an employee's pending leave request.
    """

    db = session()

    try:
        leave_request = (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.request_id == request_id,
                LeaveRequest.employee_id == employee_id
            )
            .first()
        )

        if not leave_request:
            return {
                "error": "Leave request not found",
                "request_id": request_id,
                "employee_id": employee_id
            }

        if leave_request.status != "pending":
            return {
                "error": f"Leave request cannot be approved because its status is '{leave_request.status}'",
                "request_id": request_id
            }

        
        leave_balance = (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_request.leave_type
            )
            .first()
        )

        if not leave_balance:
            return {
                "error": "Leave balance not found",
                "employee_id": employee_id,
                "leave_type": leave_request.leave_type
            }

        remaining_days = (
            leave_balance.total_days - leave_balance.used_days
        )

        if remaining_days < leave_request.number_of_days:
            return {
                "error": "Insufficient leave balance",
                "employee_id": employee_id,
                "leave_type": leave_request.leave_type,
                "remaining_days": float(remaining_days),
                "requested_days": float(leave_request.number_of_days)
            }

        leave_request.status = "approved"
        leave_request.updated_at = datetime.now()

        leave_balance.used_days += leave_request.number_of_days

        db.commit()

        db.refresh(leave_request)
        db.refresh(leave_balance)

        return {
            "message": "Leave request approved successfully",
            "request_id": leave_request.request_id,
            "employee_id": leave_request.employee_id,
            "leave_type": leave_request.leave_type,
            "number_of_days": float(leave_request.number_of_days),
            "status": leave_request.status,
            "remaining_days": float(
                leave_balance.total_days - leave_balance.used_days
            )
        }

    except Exception as e:
        db.rollback()

        return {
            "error": "Failed to approve leave request",
            "details": str(e)
        }

    finally:
        db.close()


def approve_leave_request(employee_id: str,request_id: int) -> dict:
    """
    Approve an employee's pending leave request.
    """

    db = session()

    try:
        leave_request = (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.request_id == request_id,
                LeaveRequest.employee_id == employee_id
            )
            .first()
        )

        if not leave_request:
            return {
                "error": "Leave request not found",
                "request_id": request_id,
                "employee_id": employee_id
            }

        if leave_request.status != "pending":
            return {
                "error": f"Leave request cannot be approved because its status is '{leave_request.status}'",
                "request_id": request_id
            }

        leave_balance = (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_request.leave_type
            )
            .first()
        )

        if not leave_balance:
            return {
                "error": "Leave balance not found",
                "employee_id": employee_id,
                "leave_type": leave_request.leave_type
            }

        
        remaining_days = (
            leave_balance.total_days - leave_balance.used_days
        )

        if remaining_days < leave_request.number_of_days:
            return {
                "error": "Insufficient leave balance",
                "employee_id": employee_id,
                "leave_type": leave_request.leave_type,
                "remaining_days": float(remaining_days),
                "requested_days": float(leave_request.number_of_days)
            }

        leave_request.status = "approved"
        leave_request.updated_at = datetime.now()


        leave_balance.used_days += leave_request.number_of_days

        db.commit()

        db.refresh(leave_request)
        db.refresh(leave_balance)

        return {
            "message": "Leave request approved successfully",
            "request_id": leave_request.request_id,
            "employee_id": leave_request.employee_id,
            "leave_type": leave_request.leave_type,
            "number_of_days": float(leave_request.number_of_days),
            "status": leave_request.status,
            "remaining_days": float(
                leave_balance.total_days - leave_balance.used_days
            )
        }

    except Exception as e:
        db.rollback()

        return {
            "error": "Failed to approve leave request",
            "details": str(e)
        }

    finally:
        db.close()


def reject_leave_request(employee_id: str,request_id: int) -> dict:
    """
    Reject an employee's pending leave request.
    """

    db = session()

    try:
        leave_request = (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.request_id == request_id,
                LeaveRequest.employee_id == employee_id
            )
            .first()
        )

        if not leave_request:
            return {
                "error": "Leave request not found",
                "request_id": request_id,
                "employee_id": employee_id
            }

        if leave_request.status != "pending":
            return {
                "error": f"Leave request cannot be rejected because its status is '{leave_request.status}'",
                "request_id": request_id
            }

       
        leave_request.status = "rejected"
        leave_request.updated_at = datetime.now()

        db.commit()
        db.refresh(leave_request)

        return {
            "message": "Leave request rejected successfully",
            "request_id": leave_request.request_id,
            "employee_id": leave_request.employee_id,
            "leave_type": leave_request.leave_type,
            "number_of_days": float(leave_request.number_of_days),
            "status": leave_request.status
        }

    except Exception as e:
        db.rollback()

        return {
            "error": "Failed to reject leave request",
            "details": str(e)
        }

    finally:
        db.close()