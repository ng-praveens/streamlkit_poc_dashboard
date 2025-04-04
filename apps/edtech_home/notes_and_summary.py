import streamlit as st

# Set the title and sidebar message
# st.title("Notes and Summary.")
st.sidebar.success("You are currently viewing the Notes and Summary page")

def display_notes():
    # Display the summary and notes if they are available
    st.header("Summary")
    data = st.session_state.get('data', {})

    # Ensure 'Summary' exists in data
    if 'Summary' in data:
        st.write(data['Summary'])
    else:
        st.write("Summary data is not available.")

    # Display the notes in Markdown format
    st.header("Notes")
    notes = st.session_state.get('notes', "")
    if notes:
        st.markdown(notes)
    else:
        st.write("No notes are available.")

# Check if the required data is in the session state
if "data" in st.session_state and "notes" in st.session_state:
    display_notes()
else:
    st.write("No data available to display. Please upload a file and process it to generate summary and notes. if already uploaded file wait till response is displayed")



