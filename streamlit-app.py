import openai
import shutil
import time
import datetime
import streamlit as st
from ulid import ULID
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.document_loaders import YoutubeLoader

main_save_dir = "downloads/youtube"
youtube_lang = ["en", "es", "fr", "it", "ko", "ja"]


@st.cache_data(show_spinner=False, persist=True)
def transcriptFromAudio(link: str, openai_api_key: str, save_dir: str):
    loader = GenericLoader(
        YoutubeAudioLoader([link], save_dir),
        OpenAIWhisperParser(openai_api_key),
    )
    return loader.load()


@st.cache_data(show_spinner=False, persist=True)
def transcriptFromSubtitle(link: str, lang: str):
    loader = YoutubeLoader.from_youtube_url(link, language=lang, translation=lang)
    return loader.load()


def disable():
    st.session_state.disabled = True


def enable():
    st.session_state.disabled = False


if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "ulid" not in st.session_state:
    st.session_state.ulid = str(ULID())

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

st.title("Youtube transcript")

with st.form("form"):
    print(f"OPENAI_API_KEY: {openai_api_key}")
    option = st.selectbox(
        "transcript from", ("Audio (using OpenAI Whisper API)", "Subtitle")
    )
    lang = st.selectbox("language (only work in Subtitle mode)", youtube_lang)
    link = st.text_input("Enter youtube link")
    submitted = st.form_submit_button(
        "Submit", on_click=disable, disabled=st.session_state.disabled
    )
    if submitted:
        start_time = time.time()
        try:
            st.video(link)
            with st.spinner():
                if option == "Subtitle":
                    docs = transcriptFromSubtitle(link, lang)
                else:
                    save_dir = "downloads/youtube/" + st.session_state.ulid
                    docs = transcriptFromAudio(link, openai_api_key, save_dir)
            st.markdown(docs[0].page_content)
        except Exception as e:
            if option == "Subtitle":
                st.error(e)
            else:
                if openai_api_key:
                    st.error(e)
                else:
                    st.error("Put OpenAI API Key on left sidebar")
            print(e)
        finally:
            try:
                if option != "Subtitle":
                    shutil = shutil.rmtree(save_dir)
            except:
                print(f"remove file failed: {link}")
            end_time = time.time()
            sec = end_time - start_time
            print(
                f"{datetime.datetime.now()}\tfinished in {datetime.timedelta(seconds=sec)}"
            )

st.button("Reset", on_click=enable, disabled=not st.session_state.disabled)
