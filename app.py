import streamlit as st
import json

st.set_page_config(
    page_title="등교 체크리스트",
    page_icon="🌤️",
    layout="centered"
)

# 그냥 전체 json 뱉는 함수
def load_data():
    with open("to_do.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
        return tasks

# 그냥 data에 있는 거 idx쪽에 추가하는 함수
def save_task(data, idx):
    tasks = load_data()
    for i in tasks:
        if data in tasks[i]:
            return False
    tasks[idx].append(data)
    with open("to_do.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    st.session_state.task_checked[data] = False

# 그냥 idx에 있는 data 지우는 함수
def remove_task(data, idx):
    tasks = load_data()
    tasks[idx].remove(data)
    with open("to_do.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

daily_tasks = load_data()["daily_tasks"]
all_tasks = daily_tasks

if not "task_checked" in st.session_state:
    st.session_state.task_checked = {}
    for task in all_tasks:
        st.session_state.task_checked[task] = False
if not "stage" in st.session_state:
    st.session_state.stage = "HOME"

# 누르면 취소선 생기고 해제 못하는 체크박스 생기는 함수
def checkbox_line(label):
    if not st.session_state.task_checked[label]:
        if st.checkbox(label):
            st.session_state.task_checked[label] = True
            st.rerun()
    else:
        st.checkbox(f'~~{label}~~', value=True, disabled=True)

# ---------------------------------------------------------------------
# stage HOME

if st.session_state.stage == "HOME":
    st.subheader("오늘 할 일")

    for task in daily_tasks:
        checkbox_line(task)

    # 체크박스 초기화 버튼과 우측 정렬 (EM SPACE로 간격 맞춤)
    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        if st.button("↺ 체크박스 초기화"):
            st.session_state.task_checked = {}
            for task in all_tasks:
                st.session_state.task_checked[task] = False
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

    # 할일 추가/삭제하면 표시되는 토스트
    if st.session_state.get("toast_add", False):
        st.toast(f"'{st.session_state.toast_add}' 할 일을 추가했습니다!")
        del st.session_state.toast_add

    if st.session_state.get("toast_remove", False):
        st.toast(f"'{st.session_state.toast_remove}' 할 일을 삭제했습니다!")
        del st.session_state.toast_remove

    # 제목, 뒤로가기 버튼
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("할 일 편집")
    with col2:
        if st.button("↩ 돌아가기"):
            st.session_state.stage = "HOME"
            st.rerun()

    # 할 일 표시와 삭제 버튼
    for i, task in enumerate(daily_tasks):
        col1, col2, = st.columns([10, 1], vertical_alignment="center")
        with col1:
            st.checkbox(f'**{task}** - *매일 반복*')
        with col2:
            if st.button("삭제", key=f"delete_{i}", type="primary"):
                remove_task(task, "daily_tasks")
                st.session_state.toast_remove = task
                st.rerun()

    st.subheader("")

    # 할 일 추가
    st.subheader("할 일 추가")
    repetitions = ["매일 반복", "특정 요일마다 반복", "며칠마다 반복", "반복하지 않음"]
    repetition_type = st.selectbox("얼마나 반복할 건가요?", repetitions)

    # 매일 반복
    if repetition_type == "매일 반복":

        new_task = st.text_input("무슨 일을 해야 하나요?", value="")

        col1, col2 = st.columns([4, 1])
        with col1:
            pass
        with col2:
            add_new_task = st.button("✚ 할 일 추가", type="primary")
        if add_new_task:
            if new_task:
                if save_task(new_task, "daily_tasks") == False:
                    st.error("이미 있는 할 일입니다!")
                else:
                    st.session_state.toast_add = new_task
                    st.rerun()
            else:
                st.error("할 일을 적어주세요!")