import streamlit as st

def main():
    st.set_page_config(page_title="STRIVE Pro", page_icon="🧠")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("STRIVE Pro - Login")
        
        if st.button("Demo Mode"):
            st.session_state.logged_in = True
            st.rerun()
    else:
        st.title("STRIVE Pro Dashboard")
        st.success("Welcome to STRIVE Pro! 🎉")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()