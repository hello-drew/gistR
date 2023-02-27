import os

from math import ceil
from pathlib import Path

import requests
import streamlit as st
import fitz

from image_extractor import get_images_from_pdf
from torch_summarization_model import transform_text, load_models
from utils import (
    return_size_of_object,
    clean_html,
    capitalize_each_sentence,
    capitalize_first_letter,
    remove_duplicate_sentences,
    chunk_sentences_into_list,
    count_words_in_string
)

DEFAULT_SENTENCES_IN_CHUNK = 30

MIN_SENTENCE_LENGTH = 80

def load_state(key, placeholder = 0):
    return st.session_state[key] if key in st.session_state else placeholder

def set_session_state_key(key, value) -> bool:
    st.session_state[key] = value

def create_space(size: int = 1):
    size_range = range(size)
    for _ in size_range:
        st.write("")

def return_download_button(image_bytes, filename: str):
    path = Path(filename)
    return st.download_button(
        label="Download image",
        data=image_bytes,
        file_name=filename,
        key=path.stem,
        mime=f"image/{path.suffix[1:]}"
    )

def return_image(image_tuple: tuple):
    create_space(1)
    image_bytes, image, filename = image_tuple
    filename_stem = Path(filename).stem
    page_str = get_page_image_str(filename_stem)
    image_size = return_size_of_object(image_bytes)
    col1, col2 = st.columns(2)
    with col1:
        st.image(image=image, caption=page_str)
    with col2:
        st.markdown(f"### {filename}")
        st.text(image_size)
        return_download_button(image_bytes, filename)
    create_space(1)
    return None

def upload_pdf_file():
    uploaded_pdf = st.file_uploader(label="PDF Upload", key="pdf-upload", type=['pdf'], label_visibility="hidden")
    if uploaded_pdf is not None:
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        return doc
    
def get_pdf_from_link():
    url_link = st.text_input(label="Enter PDF URL Link", key="url-link", label_visibility="hidden")
    if url_link:
        response = requests.get(url_link)
        if check_if_url_exists(response) and check_file_extension(url_link):
            doc = fitz.open(stream=response.content, filetype="pdf")
            return doc
        return None
    
def check_file_extension(url_link: str, ext_match: list = [".pdf"]):
    suffix = Path(url_link).suffix
    ext_joined = " OR ".join(ext_match)
    if suffix in ext_match:
        st.success(f"Web link is correct file type [{ext_joined}]")
        return True
    st.warning(f"Web link entered is not correct file type [{ext_joined}]")
    return False

def check_if_url_exists(response):
    with st.spinner("Checking web link is valid"):
        response_code = response.status_code == 200
        if response_code:
            st.success("Web link is valid")
            return True
        st.warning("Web link is not valid.")
        return False

def get_page_image_str(filename_stem: str) -> str:
    _, page_number, image_order = filename_stem.split("_")
    return f"Page: {page_number} | Image Order: {image_order}"

def return_progress_pct(total_size, iter) -> float:
    return ceil((100 / total_size) * iter)

def return_pdf_data(pdf_file, pdf_link):
    if not any([pdf_file, pdf_link]):
        return None
    elif pdf_file and not pdf_link:
        return pdf_file
    elif pdf_link and not pdf_file:
        return pdf_link
    else:
        st.warning("You have uploaded both a pdf file and a pdf link. Please choose one.")
        return None

def get_text_data_from_pdf(pdf_data, temp_filename_prefix: str = "temp"):
    temp_filename = f"{temp_filename_prefix}.txt"
    out = open(temp_filename, "wb")  # open text output
    for page in pdf_data:  # iterate the document pages
        text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
        out.write(text)  # write text of page
        out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
    out.close()
    with open(temp_filename) as f:
        text = f.read()
    os.remove(temp_filename)
    return text

def image_extraction_component(pdf_data, verbose: bool):
    if st.button("Extract Images", key="image-extraction"):
        image_container = []
        image_container = get_images_from_pdf(pdf_data, verbose=verbose)
        number_of_images = len(image_container)
        image_progress_bar = st.progress(0, f"Image 0 of {number_of_images}")
        image_iterator = 0
        if number_of_images > 0:
            with st.expander("Extracted Images", expanded=True):
                for image_tuple in image_container:
                    return_image(image_tuple)
                    image_iterator += 1
                    pct_progress = return_progress_pct(number_of_images, image_iterator)
                    image_progress_bar.progress(pct_progress, f"Image {image_iterator} of {number_of_images}")
        else:
            st.warning("No images to extract")

def text_summary_component(pdf_data):

    if st.button("Summarise Text", key="summarise-text"):
        text = get_text_data_from_pdf(pdf_data)
        tokenizer, model = load_models()
        with st.spinner("Summarising Text"):
            transformed_chunks = summarize_chunks(text, tokenizer, model, DEFAULT_SENTENCES_IN_CHUNK)
        download_summary_button(transformed_chunks)

SUMMARY_TEXT = "Sentences have been grouped into chunks of size {}. There are a total of {} chunks."


def summarize_chunks(text_data, tokenizer, model, chunk_size) -> str:
    text_chunks = chunk_sentences_into_list(text_data, chunk_size)
    total_chunks = len(text_chunks)
    transformed_chunks = []
    st.caption(SUMMARY_TEXT.format(chunk_size, total_chunks))
    progress_bar = st.progress(0)
    for count, text_chunk in enumerate(text_chunks):
        sentence_length = count_words_in_string(text_chunk)
        if sentence_length > MIN_SENTENCE_LENGTH:
            transformed_text = transform_text(text_chunk, tokenizer, model, sentence_length, MIN_SENTENCE_LENGTH)
            formatted_text = clean_html(transformed_text)
            formatted_text = capitalize_each_sentence(formatted_text)
            formatted_text = capitalize_first_letter(formatted_text)
            formatted_text = remove_duplicate_sentences(formatted_text)
            transformed_chunks.append(formatted_text)
        progress_count = count + 1
        progress = return_progress_pct(total_chunks, progress_count)
        progress_bar.progress(progress, f"Chunk {progress_count} of {total_chunks}")
    for transformed_chunk in transformed_chunks:
        st.markdown(transformed_chunk)
    return transformed_chunks

def download_summary_button(transformed_chunks: list):
    full_text = " \n".join(transformed_chunks)
    st.download_button(
        label="Download Summary",
        data=full_text,
        file_name="pdf_text_summary.txt",
        key="download-summary"
    )