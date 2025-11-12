import streamlit as st
from sql_session import *
from streamlit_ace import st_ace

st.title("SQL Interview Helper")
with st.sidebar:
    st.link_button("View the GitHub repository", "https://github.com/jacquelinekclee/sql-interview-helper-streamlit/tree/main", icon="📁")
    st.link_button("View my portfolio", "https://jacquelinekclee.github.io/", icon = "👩🏻‍💻")
    st.link_button("Connect with me on LinkedIn", "https://jacquelinekclee.github.io/", icon = "🤝")

def clear_new_exercise():
    '''
    reset session state for choosing new SQL topic/exercise. maintains SQL session.
    '''
    st.session_state.topic_choice = None
    st.session_state['user_sql_query'] = None
    st.session_state['exercise_returned'] = False
    st.session_state['topic_selected'] = False

def clear_try_again():
    '''
    clear user SQL query and feedback from session state while maintaining 
    original exercise
    '''
    st.session_state['user_sql_query'] = None

sql_topics = ('Retrieve data from tables',
              'Boolean and Relational Operators',
              'Wildcard and Special operators',
              'Aggregate Functions',
              'Formatting query output',
              'SQL JOINS')

try_exercise = False

session_state_variables = ['topic_selected', 'exercise_returned',
                           'sql_instance', 'results', 'user_query_submitted', 
                           'try_again', 'evaluated']

# Initialize session state
def initialize_session_state(vars):
    '''
    iterate through provided variables and initialize them as None if
    they don't exist
    Args:
        vars (list): list of strings with session state variable names
    '''
    for var in vars:
        if var not in st.session_state:
            st.session_state[var] = None

initialize_session_state(session_state_variables)

# user chooses topic
with st.form("topic"):
    # choose topic
    topic_select_message = "Choose the topic you want to practice:"
    sql_topic = st.selectbox(topic_select_message, sql_topics, index=None, 
                             placeholder = "Choose a topic", key="topic_choice")
    if st.form_submit_button("Submit topic"):
        st.session_state['topic_selected'] = True

# get SQL exercise details
if st.session_state['topic_selected'] and not st.session_state['exercise_returned']:
    # create new SQL session if needed
    if not st.session_state['sql_instance']:
        sql_session = SQLSession(sql_topic)
        st.session_state['sql_instance'] = sql_session
    else:
        sql_session = st.session_state['sql_instance']
    results = sql_session.get_sql_exercise(sql_topic)
    st.session_state['results'] = results
    st.session_state['exercise_returned'] = True

# display SQL exercise details 
if st.session_state['exercise_returned']:   
    with st.form("exercise_details"):
        st.write("SQL Question:")
        st.write(st.session_state['results']['prompt'])
        # display sample tables
        sample_tables_message = "See sample table(s) below. Be sure to scroll \
            up/down and left/right if needed:"
        st.write(sample_tables_message)
        tables = st.session_state['results']['tables']
        for table in tables:
            st.write(table)
            st.html(tables[table])
        # format code editor for user 
        input_instructions = "--Click the Apply button once completed.\n--Then, click Evaluate.\n"
        user_sql_query = st_ace(value = input_instructions,
                                placeholder = "Enter your SQL query here",
                                language = "sql", theme = "monokai", min_lines = 5,
                                key = "user_sql_query")
        if user_sql_query:
            st.session_state['user_query_submitted'] = True
        evaluate = st.form_submit_button("Evaluate?")
        if evaluate:
            final_user_sql_query = user_sql_query[len(input_instructions):].strip()
            st.session_state['evaluated'] = True
            results = st.session_state['results']
            # show example solution 
            st.write("Example Solution:")
            st.code(results['solution'], language = 'sql')
    col1, col2 = st.columns(2)
    with col1:
        clear = st.button("Try a new exercise", on_click=clear_new_exercise)
    # only show try again button if evaluation/solution was shown
    if st.session_state['evaluated']:
        with col2:
            try_again = st.button("Try again?", on_click=clear_try_again)
