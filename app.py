import streamlit as st

st.title("🎯 NEXT JACKPOT")
st.write("Upload your Powerball or Mega Millions Excel file to predict numbers.")

uploaded_file = st.file_uploader("Choose your lottery Excel file (.xlsx)")

if uploaded_file is not None:
    st.success("File uploaded! You can now build predictions here.")


