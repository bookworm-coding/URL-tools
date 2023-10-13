from __future__ import unicode_literals

from requests import get
import streamlit as st
import qrcode as qr
import yt_dlp as yt
from os import remove
from os.path import isfile
from ffmpeg import FFmpeg

st.set_page_config(
    page_title="URL 도구상자",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "This app is made by [bookworm-coding](https://github.com/bookworm-coding)"
    }
)

st.title('URL 도구')

bar = None
status = None
filename: str = ""


def url_shorten():
    if url == "" or url is None:
        st.error("URL을 입력해주세요!")
        return
    response = get("https://vo.la/api/?key="+st.secrets["API key"]+"&url=" + url)
    data = response.json()
    st.info("단축된 URL : " + data["short"])
    return


def qr_code():
    if url == "" or url is None:
        st.error("URL을 입력해주세요!")
        return
    q = qr.make(url)
    st.image(q.get_image())
    q.save("qrcode.png")
    with open("qrcode.png", "rb") as file:
        st.download_button("QR코드 PNG 다운로드", file, "QRcode.png", "image/png")
    remove("qrcode.png")
    return


def audio():
    global bar, filename, status
    bar = st.progress(0, text="파일 준비 중입니다...잠시만 기다려주세요...")
    status = st.status(label="파일 준비 중입니다...잠시만 기다려주세요...", expanded=True)

    ydl_opts = {
        'ignoreerrors': True,
        'nooverwrites': True,
        'format': '251',
        'outtmpl': "%(fulltitle)s.mp3",
        'noplaylist': True,
        'lazy_playlist': True,
        'merge_output_format': 'mp3',
        'audioquality': '0',
        'audioformat': 'mp3',
        'addmetadata': True,
        'extractaudio': True,
        'embedthumnail': True,
        'quiet': True,
        'progress_hooks': [hook],
    }
    with yt.YoutubeDL(ydl_opts) as ydl:
        ydl.download([str(url)])
    while not isfile(filename):
        pass
    ffmpeg = (
        FFmpeg()
        .input(filename)
        .output("temp.wav")
    )
    ffmpeg.execute()
    bar.empty()
    status.update(label="다운로드 완료", state="complete", expanded=False)
    st.audio("temp.wav")
    remove("temp.wav")
    st.download_button("다운로드", data=filename, file_name=filename, mime="audio/mpeg", on_click=st.empty)
    remove(filename)
    return


def hook(d):
    global bar, filename, status
    if d['status'] == 'error':
        status.update(label="오류 발생", state="error", expanded=False)
        st.rerun()
        return
    try:
        filename = d['filename']
    except Exception:
        pass
    try:
        bar.progress(float(d["_percent_str"][:-1]) / 100.0, "파일 준비 중입니다...잠시만 기다려주세요...")
        status.write("[download]" + d['_default_template'])
    except Exception:
        pass


def video():
    global bar, filename, status
    bar = st.progress(0, text="파일 준비 중입니다...잠시만 기다려주세요...")
    status = st.status(label="파일 준비 중입니다...잠시만 기다려주세요...", expanded=True)

    ydl_opts = {
        'ignoreerrors': True,
        'nooverwrites': True,
        'format': 'bestvideo[vcodec=h264]+bestaudio[acodec=aac]/best/best',
        'outtmpl': '%(fulltitle)s.mp4',
        'noplaylist': True,
        'lazy_playlist': True,
        'merge_output_format': 'mp4',
        'audioquality': '0',
        'audioformat': 'best',
        'addmetadata': False,
        'extractaudio': False,
        'embedthumnail': False,
        'quiet': True,
        'progress_hooks': [hook],
    }
    with yt.YoutubeDL(ydl_opts) as ydl:
        ydl.download([str(url)])
    while not isfile(filename):
        pass
    bar.empty()
    status.update(label="다운로드 완료", state="complete", expanded=False)
    st.video(data=filename)
    st.download_button("다운로드", data=filename, file_name=filename, mime="video/mp4", on_click=st.empty)
    remove(filename)
    return


url = st.text_input("URL을 입력하세요")
col1, col2, col3, col4 = st.columns([4, 5, 6, 6])
with col1:
    button1 = st.button("URL 단축하기", on_click=url_shorten)
with col2:
    button2 = st.button("QR코드 생성하기", on_click=qr_code)
with col3:
    button3 = st.button("유튜브 동영상 다운로드", on_click=video)
with col4:
    button4 = st.button("유튜브 오디오 다운로드", on_click=audio)