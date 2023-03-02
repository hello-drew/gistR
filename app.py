import streamlit as st
from helpers import (
    upload_pdf_file, 
    create_space, 
    image_extraction_component, 
    get_pdf_from_link, 
    return_pdf_data, 
    text_summary_component,
    set_session_state_key,
    sidebar_widget,
    get_text_data_from_pdf,
    load_state,
    load_pdf_report_summary
)

from config import PDF_DATA_KEY, TEXT_DATA_KEY

st.set_page_config(
    page_title="GistR",
    page_icon="📝", 
    layout="centered", 
    initial_sidebar_state="auto",
)

pdf_data = set_session_state_key(PDF_DATA_KEY, None)
text_data = load_state(TEXT_DATA_KEY, "")

st.header("📝 GistR | PDF Summary & Image Extraction")

create_space(1)
with st.expander(label="How to use GistR", expanded=True):
    st.markdown("""

    1) Upload a PDF file or a valid PDF url

    2) Change the settings in the sidebar (optional)

    3) Click on the "Extract Images" button to see all images in the document

    4) Click on the "Download Image" button to select the image(s) you would like to download

    5) Click on the "Summarise Text" button to run the AI model on the PDF text (may take a while depending on the length of the file)

    6) Click on "Download Summary" to download the summary as a .txt file
    """)
"---"
create_space(1)
st.markdown("##### Upload A PDF File")
pdf_file = upload_pdf_file()
st.markdown("#### OR")
st.markdown("##### Input A PDF URL")
st.caption("The link should be a pure http(s) path and should end in .pdf")

pdf_link = get_pdf_from_link()
pdf_data = return_pdf_data(pdf_file, pdf_link)

sidebar_widget()

create_space(1)

if pdf_data:
    get_text_data_from_pdf(pdf_data)
    load_pdf_report_summary()
    "---"
    st.markdown("#### Image Extraction")
    image_extraction_component(pdf_data, verbose=False)
    create_space(1)


    st.markdown("#### Text Summary")
    text_summary_component()
    create_space(1)
    "---"

st.caption("GistR does not store your uploaded PDF data on our servers or claim ownership of any of the text and image rights within the PDF documents uploaded by users ✌️")
st.caption("Made in London with ❤️ | Buy me a [ko-fi](https://ko-fi.com/hidrew) to say thanks 🫡")
