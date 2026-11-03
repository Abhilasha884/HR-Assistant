
import streamlit as st
import requests
from datetime import date

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="NovaTech HR Portal",
    page_icon="🏢",
    layout="wide"
)


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "employee_id" not in st.session_state:
    st.session_state.employee_id = None

if "employee" not in st.session_state:
    st.session_state.employee = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def api_get(endpoint):
    """Make a GET request to FastAPI."""
    try:
        response = requests.get(
            f"{FASTAPI_URL}{endpoint}",
            timeout=15
        )
        return response

    except requests.exceptions.Timeout:
        st.error(f"Request timed out while accessing {endpoint}.")
        return None

    except requests.exceptions.ConnectionError as exc:
        st.error("Could not connect to FastAPI.")
        st.code(str(exc))
        return None

    except requests.exceptions.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None


def logout():
    """Close the active HR session and clear UI state."""

    session_id = st.session_state.session_id

    if session_id is not None:
        try:
            response = requests.put(
                f"{FASTAPI_URL}/sessions/{session_id}/close",
                timeout=15
            )

            if response.status_code != 200:
                st.error(
                    f"Could not close session: {response.text}"
                )
                return

        except requests.exceptions.RequestException as exc:
            st.error("Could not connect to FastAPI to close the session.")
            st.code(str(exc))
            return

    st.session_state.session_id = None
    st.session_state.employee_id = None
    st.session_state.employee = None
    st.session_state.messages = []
    st.session_state.current_page = "Dashboard"

    if "leave_success" in st.session_state:
        del st.session_state["leave_success"]

    st.rerun()


def show_error_response(response, not_found_message):
    """Display a readable message for an API response."""

    if response is None:
        return

    if response.status_code == 404:
        st.info(not_found_message)

    elif not response.ok:
        st.error(f"API error ({response.status_code})")
        st.code(response.text)


def show_leave_balances(employee_id):
    """Fetch and display the employee's leave balances."""

    response = api_get(
        f"/employees/{employee_id}/leave-balance"
    )

    if response is None:
        return

    if response.status_code == 404:
        st.info("No leave balances found.")
        return

    if not response.ok:
        show_error_response(
            response,
            "No leave balances found."
        )
        return

    try:
        balances = response.json()
    except ValueError:
        st.error("FastAPI returned an invalid leave-balance response.")
        return

    if not balances:
        st.info("No leave balances found.")
        return

    columns = st.columns(len(balances))

    for column, balance in zip(columns, balances):
        total = float(balance.get("total_days") or 0)
        used = float(balance.get("used_days") or 0)
        remaining = total - used

        with column:
            st.metric(
                label=f"{balance.get('leave_type', 'Leave')} Remaining",
                value=f"{remaining:g} days",
                delta=f"{used:g} used out of {total:g} days"
            )


# ---------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------

if st.session_state.session_id is None:

    st.markdown(
        """
        <div style="text-align:center; padding-top:70px;">
            <h1>🏢 NovaTech HR Portal</h1>
            <p style="font-size:18px;">
                Enterprise HR Policy & Employee Assistant
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Employee Login")

        user_id = st.text_input(
            "User ID",
            placeholder="Enter your employee ID"
        ).strip()

        st.caption(
            "Prototype login: your User ID is your Employee ID. "
            "Password/JWT authentication has not been implemented yet."
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not user_id:
                st.warning("Please enter your User ID.")

            else:
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/sessions",
                        json={"employee_id": user_id},
                        timeout=15
                    )

                    if response.status_code not in (200, 201):
                        st.error(
                            f"Login failed ({response.status_code})"
                        )
                        st.code(response.text)

                    else:
                        session_data = response.json()
                        session_id = session_data["session_id"]
                        employee_id = session_data["employee_id"]

                        employee_response = requests.get(
                            f"{FASTAPI_URL}/employees/{employee_id}",
                            timeout=15
                        )

                        if employee_response.status_code != 200:

                            try:
                                requests.put(
                                    f"{FASTAPI_URL}/sessions/"
                                    f"{session_id}/close",
                                    timeout=15
                                )
                            except requests.exceptions.RequestException:
                                pass

                            st.error(
                                "The employee session was created, but "
                                "the employee profile could not be loaded."
                            )
                            st.code(employee_response.text)

                        else:
                            st.session_state.session_id = session_id
                            st.session_state.employee_id = employee_id
                            st.session_state.employee = employee_response.json()
                            st.session_state.messages = []
                            st.session_state.current_page = "Dashboard"

                            st.rerun()

                except requests.exceptions.Timeout:
                    st.error("Login request timed out.")

                except requests.exceptions.ConnectionError as exc:
                    st.error("Could not connect to FastAPI.")
                    st.code(str(exc))

                except (requests.exceptions.RequestException,
                        ValueError, KeyError) as exc:
                    st.error(f"Login failed: {exc}")


# ---------------------------------------------------------
# HR PORTAL
# ---------------------------------------------------------

else:

    employee = st.session_state.employee
    employee_id = st.session_state.employee_id

    # -----------------------------------------------------
    # Sidebar: Employee Profile and Navigation
    # -----------------------------------------------------

    with st.sidebar:

        st.markdown("## 🏢 NovaTech HR")
        st.divider()

        if employee:
            st.markdown(
                f"### 👤 {employee.get('full_name', 'Employee')}"
            )

            st.write(f"**Employee ID:** {employee_id}")
            st.write(
                f"**Department:** {employee.get('department') or '-'}"
            )
            st.write(
                f"**Designation:** {employee.get('designation') or '-'}"
            )

        else:
            st.write(f"**Employee ID:** {employee_id}")

        st.divider()
        st.markdown("### Navigation")

        navigation = [
            ("🏠 Dashboard", "Dashboard"),
            ("📅 Leave", "Leave"),
            ("💰 Payroll", "Payroll"),
            ("🎉 Holidays", "Holidays"),
            ("🤖 HR Assistant", "HR Assistant")
        ]

        for label, page_name in navigation:
            if st.button(
                label,
                use_container_width=True,
                key=f"nav_{page_name}"
            ):
                st.session_state.current_page = page_name
                st.rerun()

        st.divider()

        if st.button("Logout", use_container_width=True):
            logout()

    # -----------------------------------------------------
    # Main Header
    # -----------------------------------------------------

    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.title("NovaTech HR Portal")

        if employee:
            st.write(
                f"Welcome, **{employee.get('full_name', 'Employee')}** 👋"
            )
        else:
            st.write(f"Welcome, **{employee_id}** 👋")

    with header_col2:
        st.metric("Employee ID", employee_id)

    st.divider()

    # -----------------------------------------------------
    # Dashboard
    # -----------------------------------------------------

    page = st.session_state.current_page

    if page == "Dashboard":

        st.subheader("🏠 Employee Dashboard")
        st.write("Your HR information at a glance.")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info("📅 **Leave**\n\nView your leave balance and requests.")

        with col2:
            st.info("💰 **Payroll**\n\nView your latest payroll.")

        with col3:
            st.info("🎉 **Holidays**\n\nView company holidays.")

        with col4:
            st.info("🤖 **HR Assistant**\n\nAsk questions about HR.")

        st.divider()
        st.subheader("Quick Overview")

        show_leave_balances(employee_id)

        st.write("")

        if st.button("Open HR Assistant", type="primary"):
            st.session_state.current_page = "HR Assistant"
            st.rerun()

    # -----------------------------------------------------
    # Leave Management
    # -----------------------------------------------------

    elif page == "Leave":

        st.subheader("📅 Leave Management")

        st.markdown("### My Leave Balances")
        show_leave_balances(employee_id)

        st.divider()
        st.markdown("### 📝 Apply for Leave")

        with st.form("apply_leave_form", clear_on_submit=True):

            leave_type = st.selectbox(
                "Leave Type",
                options=[
                    "Earned Leave",
                    "Casual Leave",
                    "Sick Leave"
                ]
            )

            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=date(2026, 11, 2)
                )

            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=date(2026, 11, 3)
                )

            number_of_days = st.number_input(
                "Number of Leave Days",
                min_value=1,
                max_value=365,
                value=2,
                step=1
            )

            reason = st.text_area(
                "Reason for Leave",
                placeholder="Enter your reason for leave (optional)"
            )

            submitted = st.form_submit_button(
                "Submit Leave Request",
                type="primary",
                use_container_width=True
            )

            if submitted:

                if end_date < start_date:
                    st.error(
                        "End date must be on or after the start date."
                    )

                else:
                    calendar_days = (
                        end_date - start_date
                    ).days + 1

                    if number_of_days > calendar_days:
                        st.error(
                            f"Number of leave days cannot exceed "
                            f"the {calendar_days} calendar days "
                            f"between the selected dates."
                        )

                    else:
                        payload = {
                            "employee_id": employee_id,
                            "leave_type": leave_type,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "number_of_days": number_of_days,
                            "reason": reason.strip() or None
                        }

                        try:
                            response = requests.post(
                                f"{FASTAPI_URL}/employees/"
                                f"{employee_id}/leave-requests",
                                json=payload,
                                timeout=30
                            )

                            if response.status_code in (200, 201):
                                st.session_state.leave_success = (
                                    "Leave request submitted successfully! "
                                    "Your request is pending approval."
                                )
                                st.rerun()

                            else:
                                st.error(
                                    "Failed to submit leave request "
                                    f"({response.status_code})."
                                )
                                st.code(response.text)

                        except requests.exceptions.Timeout:
                            st.error("Leave request timed out.")

                        except requests.exceptions.ConnectionError as exc:
                            st.error("Could not connect to FastAPI.")
                            st.code(str(exc))

                        except requests.exceptions.RequestException as exc:
                            st.error(f"Leave request failed: {exc}")

        if "leave_success" in st.session_state:
            st.success(st.session_state.leave_success)
            del st.session_state.leave_success

        st.divider()
        st.markdown("### 📋 My Leave Requests")

        request_response = api_get(
            f"/employees/{employee_id}/leave-requests"
        )

        if request_response is not None:

            if request_response.status_code == 200:

                try:
                    leave_requests = request_response.json()

                    if leave_requests:
                        st.dataframe(
                            leave_requests,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("You have no leave requests.")

                except ValueError:
                    st.error("Invalid leave-requests response from FastAPI.")

            elif request_response.status_code == 404:
                st.info("You have no leave requests yet.")

            else:
                show_error_response(
                    request_response,
                    "No leave requests found."
                )

    # -----------------------------------------------------
    # Payroll
    # -----------------------------------------------------

    elif page == "Payroll":

        st.subheader("💰 My Payroll")

        response = api_get(
            f"/employees/{employee_id}/payroll/latest"
        )

        if response is not None:

            if response.status_code == 200:

                try:
                    payroll = response.json()

                    st.write(
                        f"**Pay Period:** {payroll.get('pay_period', '-')}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Basic Salary",
                            f"{float(payroll.get('basic_salary') or 0):,.2f}"
                        )

                        st.metric(
                            "Allowances",
                            f"{float(payroll.get('allowances') or 0):,.2f}"
                        )

                    with col2:
                        st.metric(
                            "Deductions",
                            f"{float(payroll.get('deductions') or 0):,.2f}"
                        )

                        st.metric(
                            "Net Salary",
                            f"{float(payroll.get('net_salary') or 0):,.2f}"
                        )

                except (ValueError, TypeError) as exc:
                    st.error(f"Could not display payroll data: {exc}")

            elif response.status_code == 404:
                st.info("No payroll information found.")

            else:
                show_error_response(
                    response,
                    "No payroll information found."
                )

    # -----------------------------------------------------
    # Holidays
    # -----------------------------------------------------

    elif page == "Holidays":

        st.subheader("🎉 Company Holidays")

        year = st.selectbox(
            "Select Year",
            options=list(range(2026, 2031)),
            index=0
        )

        response = api_get(f"/holidays/{year}")

        if response is not None:

            if response.status_code == 200:

                try:
                    holidays = response.json()

                    if holidays:
                        st.dataframe(
                            holidays,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info(f"No holidays found for {year}.")

                except ValueError:
                    st.error("Invalid holidays response from FastAPI.")

            elif response.status_code == 404:
                st.info(f"No holidays found for {year}.")

            else:
                show_error_response(
                    response,
                    f"No holidays found for {year}."
                )

    
    # -----------------------------------------------------
    # HR Assistant
    # -----------------------------------------------------

    elif page == "HR Assistant":

        st.subheader("🤖 HR Assistant")

        st.write(
            "Ask questions about company policies, leave, payroll, "
            "holidays, and your employee information."
        )

        # Display conversation history.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_query = st.chat_input("Ask your HR question...")

        if user_query:

            st.session_state.messages.append({
                "role": "user",
                "content": user_query
            })

            with st.chat_message("user"):
                st.write(user_query)

            try:
                with st.spinner(
                    "The HR Assistant is processing your question..."
                ):

                    response = requests.post(
                        f"{FASTAPI_URL}/agent",
                        json={
                            "session_id": st.session_state.session_id,
                            "user_query": user_query
                        },
                        timeout=900
                    )

                if response.status_code == 200:

                    try:
                        data = response.json()

                    except ValueError:
                        st.error(
                            "FastAPI returned an invalid JSON response."
                        )
                        st.code(response.text)

                    else:
                        assistant_response = data.get("response")

                        if assistant_response is None:
                            st.error(
                                "The agent response does not contain "
                                "the expected response field."
                            )
                            st.json(data)

                        else:

                            # Check whether confirmation is required.
                            requires_confirmation = data.get(
                                "requires_confirmation", False
                            )

                            if requires_confirmation:

                                leave_details = data.get(
                                    "confirmation_data"
                                ) or {}

                                # Build a readable confirmation message.
                                confirmation_message = (
                                    f"{assistant_response}\n\n"
                                    f"**Leave Type:** "
                                    f"{leave_details.get('leave_type', '-')}\n\n"
                                    f"**Start Date:** "
                                    f"{leave_details.get('start_date', '-')}\n\n"
                                    f"**End Date:** "
                                    f"{leave_details.get('end_date', '-')}\n\n"
                                    f"**Number of Days:** "
                                    f"{leave_details.get('number_of_days', '-')}\n\n"
                                    f"**Reason:** "
                                    f"{leave_details.get('reason') or 'Not provided'}\n\n"
                                    "Please reply **Yes** to submit or "
                                    "**No** to cancel."
                                )

                                assistant_response = confirmation_message

                            # Save assistant response in chat history.
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_response
                            })

                            with st.chat_message("assistant"):
                                st.markdown(assistant_response)

                else:
                    st.error(
                        f"Agent request failed ({response.status_code})."
                    )
                    st.code(response.text)

            except requests.exceptions.Timeout:
                st.error(
                    "The HR Assistant took longer than 900 seconds "
                    "to respond. Check the FastAPI terminal for errors."
                )

            except requests.exceptions.ConnectionError as exc:
                st.error(
                    "Could not establish a connection to FastAPI. "
                    "Check the backend terminal."
                )
                st.code(str(exc))

            except requests.exceptions.RequestException as exc:
                st.error(f"Agent request failed: {exc}")



