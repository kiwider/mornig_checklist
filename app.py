import streamlit as st

st.set_page_config(
    page_title="등교 체크리스트",
    page_icon="🌤️",
    layout="centered"
)

if not "checkbox_max" in st.session_state:
    st.session_state.checkbox_max = 2
if not "checked" in st.session_state:
    st.session_state.checked = []
    st.session_state.checked = [False] * st.session_state.checkbox_max
if not "stage" in st.session_state:
    st.session_state.stage = "HOME"

# 누르면 취소선 생기고 해제 못하는 체크박스 생기는 함수
def checkbox_line(label, idx):
    if not st.session_state.checked[idx]:
        if st.checkbox(label):
            st.session_state.checked[idx] = True
            st.rerun()
    else:
        st.checkbox(f'~~{label}~~', value=True, disabled=True)

# ---------------------------------------------------------------------
# stage HOME

if st.session_state.stage == "HOME":
    st.subheader("오늘 할 일")
    checkbox_line("안녕하세요", 0)
    checkbox_line("반가워요", 1)

    # 체크박스 초기화 버튼과 우측 정렬 (EM SPACE로 간격 맞춤)
    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        if st.button("↺ 체크박스 초기화"):
            st.session_state.checked = []
            st.session_state.checked = [False] * st.session_state.checkbox_max
            st.rerun()

    # 할 일 추가 버튼과 우측 정렬
    col1, col2 = st.columns([4, 1])
    with col1:
        pass
    with col2:
        if st.button("✎ 할 일 편집", type="primary"):
            st.session_state.stage = "SETTING"
            st.rerun()

# ---------------------------------------------------------------------
# stage SETTING

elif st.session_state.stage == "SETTING":
    st.subheader("할 일 편집")

    # 돌아가기 버튼과 우측 정렬
    col1, col2 = st.columns([4, 1])
    with col1:
        pass
    with col2:
        if st.button("↩ 돌아가기"):
            st.session_state.stage = "HOME"
            st.rerun()