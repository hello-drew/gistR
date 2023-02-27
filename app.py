import streamlit as st
from helpers import (
    upload_pdf_file, 
    create_space, 
    image_extraction_component, 
    get_pdf_from_link, 
    return_pdf_data, 
    text_summary_component,
    set_session_state_key
)
st.set_page_config(
    page_title="GistR",
    page_icon="📝", 
    layout="centered", 
    initial_sidebar_state="collapsed",
)

st.header("GistR 📝 | PDF Summary & Image Extraction")

st.markdown("""
#### How to use GistR

1) Upload a PDF file or a valid pdf URL

2) Click on the button "Extract Images" buton to see all images in the document

3) Click on the "Download Image" button to select the image(s) you would like to download
""")

st.caption("GistR does not claim ownership of any PDF documents or assets contained.")

"---"
create_space(1)
st.markdown("##### Upload a PDF File")
pdf_file = upload_pdf_file()
st.markdown("#### OR")
st.markdown("##### Input a PDF url")
st.caption("Ensure the link is a pure http(s) link - no browser extension url prefixes - and that the url ends in .pdf")
pdf_link = get_pdf_from_link()
pdf_data = return_pdf_data(pdf_file, pdf_link)
set_session_state_key("pdf_data", pdf_data)

create_space(1)

if pdf_data:
    "---"
    st.markdown("#### Text Summary")
    text_summary_component(pdf_data)
    create_space(1)

    st.markdown("#### Image Extraction")
    image_extraction_component(pdf_data, verbose=False)
    create_space(1)
    "---"
