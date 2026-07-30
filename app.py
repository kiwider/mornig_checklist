import streamlit as st

if not "checkbox_max" in st.session_state:
    st.session_state.checkbox_max = 2
if not "checked" in st.session_state:
    st.session_state.checked = []
    st.session_state.checked = [False] * st.session_state.checkbox_max

# 누르면 취소선 생기고 해제 못하는 체크박스 생기는 함수
def checkbox_line(label, idx):
    if not st.session_state.checked[idx]:
        if st.checkbox(label):
            st.session_state.checked[idx] = True
            st.rerun()
    else:
        st.checkbox(f'~~{label}~~', value=True, disabled=True)

checkbox_line("안녕하세요", 0)
checkbox_line("반가워요", 1)

# 4:1 비율로 버튼 우측 정렬
col1, col2 = st.columns([4, 1])
with col1:
    pass
with col2:
    if st.button("체크박스 초기화"):
        st.session_state.checked = []
        st.session_state.checked = [False] * st.session_state.checkbox_max
        st.rerun()