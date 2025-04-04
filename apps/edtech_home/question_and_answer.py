import streamlit as st

st.sidebar.success("You are currently viewing the Q&A page")


def validation():
    """
    validates the user response of Q&A after submition from session state.

    Parameters:
    None

    Returns:
    None
    """
    data = st.session_state["data"]
    for idx, (q, user_answer) in enumerate(
        zip(data["Questions"], st.session_state["user_answers"]), 1
    ):
        correct_answer_index = q.get("CorrectAnswer")
        if correct_answer_index is not None:
            correct_answer = q["Options"][correct_answer_index - 1]
        else:
            correct_answer = "No correct answer provided"

        if user_answer:
            if user_answer == correct_answer:
                st.success(f"Question {idx}: Correct! The answer is {correct_answer}.")
            else:
                st.error(
                    f"Question {idx}: Incorrect. The correct answer is {correct_answer}."
                )
        else:
            st.warning(f"Question {idx}: No option selected.")


def display_qa():
    """
    Handles Q&A form and storing the response of user in session state.

    Parameters:
    None

    Returns:
    None
    """
    # Safely get data from session state, use an empty dictionary if not found
    data = st.session_state.get("data", {})

    # Check if 'Questions' exist in the data
    if "Questions" not in data:
        st.write(
            "No questions available. Please ensure that the data includes questions."
        )
        return

    # Display the questions header
    st.header("Questions")

    # Initialize session state to store user answers if not already present
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = [None] * len(data["Questions"])

    # Create a form for the questions
    with st.form("questions_form"):
        # Loop through the questions and display each one with options
        for idx, q in enumerate(data["Questions"], 1):
            st.subheader(
                f"Question {idx}: {q.get('Question', 'No question text available')}"
            )
            st.session_state["user_answers"][idx - 1] = st.radio(
                f"Select an option for Question {idx}:",
                options=q.get("Options", ["No options available"]),
                index=None,
                key=f"question_{idx}",
            )

        # Submit button for the form
        submit = st.form_submit_button("Submit All")

    # Handle form submission
    if submit:
        validation()


# Check if the required data is in the session state
if "data" in st.session_state and "Questions" in st.session_state["data"]:
    display_qa()
else:
    st.write(
        "No data available to display. Please upload a file and process it to generate Q&A. if already uploaded file wait till response is displayed"
    )
