from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st

@st.cache_resource
def load_models():
    tokenizer = AutoTokenizer.from_pretrained('t5-base')
    model = AutoModelForSeq2SeqLM.from_pretrained('t5-base', return_dict=True)
    return tokenizer, model


def transform_text(
        text_data,
        tokenizer,
        model,
        max_length: int = 512,
        min_length: int =  80,
        length_penalty: float = 10.,
        num_beams: int = 2
    ):
    prompt = f"summarize: {text_data}"
    inputs = tokenizer.encode(
        prompt,
        return_tensors='pt',
        max_length=max_length,
        truncation=True
    )
    summary_ids = model.generate(
        inputs,
        max_length=max_length,
        min_length=min_length,
        length_penalty=length_penalty,
        num_beams=num_beams
    )
    summary = tokenizer.decode(summary_ids[0])
    return summary
