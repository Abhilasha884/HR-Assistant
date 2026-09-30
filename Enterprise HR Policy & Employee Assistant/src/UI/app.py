import streamlit as st
import requests


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


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def logout():
    """Close the active HR session and clear UI state."""

    if st.session_state.session_id is not None:

        try:
            requests.put(
                f"{FASTAPI_URL}/sessions/"
                f"{st.session_state.session_id}/close"
            )
        except requests.exceptions.ConnectionError:
            pass

    st.session_state.session_id = None
    st.session_state.employee_id = None
    st.session_state.employee = None
    st.session_state.messages = []

    st.rerun()


# ---------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------

if st.session_state.session_id is None:

    st.markdown(
        """
        <div style="text-align:center; padding-top:80px;">
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
        )

        st.caption(
            "For this prototype, your User ID is your Employee ID."
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

                    # -----------------------------------------
                    # Create session
                    # User ID = Employee ID
                    # -----------------------------------------

                    response = requests.post(
                        f"{FASTAPI_URL}/sessions",
                        json={
                            "employee_id": user_id
                        }
                    )

                    if response.status_code == 200:

                        session_data = response.json()

                        st.session_state.session_id = (
                            session_data["session_id"]
                        )

                        st.session_state.employee_id = (
                            session_data["employee_id"]
                        )

                        # -------------------------------------
                        # Get employee profile
                        # -------------------------------------

                        employee_response = requests.get(
                            f"{FASTAPI_URL}/employees/"
                            f"{user_id}"
                        )

                        if employee_response.status_code == 200:

                            st.session_state.employee = (
                                employee_response.json()
                            )

                        else:

                            st.session_state.employee = None

                        st.session_state.messages = []

                        st.rerun()

                    else:

                        st.error(
                            f"Login failed: {response.text}"
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to FastAPI. "
                        "Please make sure the FastAPI server is running."
                    )


# ---------------------------------------------------------
# HR PORTAL
# ---------------------------------------------------------

else:

    employee = st.session_state.employee

    # -----------------------------------------------------
    # Sidebar
    # -----------------------------------------------------

    with st.sidebar:

        st.markdown("## 🏢 NovaTech HR")

        st.divider()

        if employee:

            full_name = employee.get(
                "full_name",
                "Employee"
            )

            department = employee.get(
                "department",
                "-"
            )

            designation = employee.get(
                "designation",
                "-"
            )

            st.markdown(
                f"### 👤 {full_name}"
            )

            st.write(
                f"**Employee ID:** "
                f"{st.session_state.employee_id}"
            )

            st.write(
                f"**Department:** {department}"
            )

            st.write(
                f"**Designation:** {designation}"
            )

        else:

            st.write(
                f"**Employee ID:** "
                f"{st.session_state.employee_id}"
            )

        st.divider()

        st.markdown("### Navigation")

        st.button(
            "🏠 Dashboard",
            use_container_width=True
        )

        st.button(
            "📅 Leave",
            use_container_width=True
        )

        st.button(
            "💰 Payroll",
            use_container_width=True
        )

        st.button(
            "🎉 Holidays",
            use_container_width=True
        )

        st.button(
            "🤖 HR Assistant",
            use_container_width=True
        )

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True
        ):

            logout()


    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    header_col1, header_col2 = st.columns(
        [4, 1]
    )

    with header_col1:

        st.title("HR Portal")

        if employee:

            st.write(
                f"Welcome, **{employee.get('full_name', 'Employee')}** 👋"
            )

        else:

            st.write(
                f"Welcome, **{st.session_state.employee_id}** 👋"
            )

    with header_col2:

        st.metric(
            "Employee ID",
            st.session_state.employee_id
        )


    st.divider()


    # -----------------------------------------------------
    # Dashboard Cards
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.info(
            "📅\n\n"
            "**Leave**\n\n"
            "View your leave balance and requests."
        )

    with col2:

        st.info(
            "💰\n\n"
            "**Payroll**\n\n"
            "View your latest payroll information."
        )

    with col3:

        st.info(
            "🎉\n\n"
            "**Holidays**\n\n"
            "View the company holiday calendar."
        )

    with col4:

        st.info(
            "🤖\n\n"
            "**HR Assistant**\n\n"
            "Ask questions about HR policies."
        )


    st.divider()


    # -----------------------------------------------------
    # HR Assistant
    # -----------------------------------------------------

    st.subheader("🤖 HR Assistant")

    st.write(
        "Ask questions about company policies, "
        "leave, payroll, holidays, and your employee information."
    )


    # -----------------------------------------------------
    # Previous Chat Messages
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(
                message["content"]
            )


    # -----------------------------------------------------
    # Chat Input
    # -----------------------------------------------------

    user_query = st.chat_input(
        "Ask your HR question..."
    )


    if user_query:

        # ---------------------------------------------
        # Show user message
        # ---------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        with st.chat_message("user"):

            st.write(user_query)


        # ---------------------------------------------
        # Call FastAPI Agent
        # ---------------------------------------------

        try:

            response = requests.post(
                f"{FASTAPI_URL}/agent",
                json={
                    "session_id": st.session_state.session_id,
                    "user_query": user_query
                }
            )


            if response.status_code == 200:

                response_data = response.json()

                assistant_response = (
                    response_data["response"]
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )

                with st.chat_message("assistant"):

                    st.write(
                        assistant_response
                    )

            else:

                st.error(
                    f"Agent request failed: "
                    f"{response.text}"
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI. "
                "Please make sure the FastAPI server is running."
            )