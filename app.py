import streamlit as st
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title="등교 체크리스트",
    page_icon="🌤️",
    layout="centered"
)

# 그냥 전체 json 중에서 tasks만 뱉는 함수
def load_task():
    with open("to_do.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
        return tasks

# 그냥 task 추가하는 함수
def save_task(name, repeat_unit, interval, start_date, other=None):
    tasks = load_task()
    names = [task["name"] for task in tasks]
    if name in names:
        return False
    new_task = {"name": name, "repeat_unit": repeat_unit,
                "interval": interval, "start_date": start_date}
    if other != None:
        new_task.update(other)
    tasks.append(new_task)
    with open("to_do.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    st.session_state.task_checked[name] = False

# 그냥 task 삭제하는 함수
def remove_task(name):
    tasks = load_task()
    for idx, task in enumerate(tasks):
        if task["name"] == name:
            tasks.pop(idx)
            break
    with open("to_do.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    del st.session_state.task_checked[name]

tasks = load_task()
task_names = [task["name"] for task in tasks]

if not "task_checked" in st.session_state:
    st.session_state.task_checked = {}
    for name in task_names:
        st.session_state.task_checked[name] = False
if "today" not in st.session_state:
    st.session_state.today = datetime.now().date()
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

    # 오늘 할 일 계산하기
    today_tasks = []
    today = st.session_state.today
    for t in tasks:
        start_date = datetime.strptime(
            t["start_date"], "%Y-%m-%d"
        ).date()
        days = (today - start_date).days
        if t["interval"] == None:
            if days == 0:
                today_tasks.append(t["name"])
        else:
            if days >= 0 and days % t["interval"] == 0:
                today_tasks.append(t["name"])

    if len(today_tasks) > 0:
        for task in today_tasks:
            checkbox_line(task)
    else:
        st.write("*오늘은 할 일이 없네요!")

    # 체크박스 초기화 버튼과 우측 정렬 (EM SPACE로 간격 맞춤)
    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        if st.button("↺ 체크박스 초기화"):
            st.session_state.task_checked = {}
            for task in task_names:
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

    # 할 일의 반복 메시지 구하기
    task_repeat_messages = {}
    for task in tasks:
        if task["repeat_unit"] == None:
            task_repeat_messages[task["name"]] = f'{task["start_date"]}에 표시, 반복 안 함'
        elif task["repeat_unit"] == "day":
            if task["interval"] == 1:
                task_repeat_messages[task["name"]] = f'{task["start_date"]}에 시작, 매일 반복'
            else:
                task_repeat_messages[task["name"]] = (
                    f'{task["start_date"]}에 시작, {task["interval"]}일마다 반복'
                )

    # 할 일 표시와 삭제 버튼
    for task in task_names:
        col1, col2, = st.columns([10, 1])
        with col1:
            st.checkbox(f'**{task}** - *{task_repeat_messages[task]}*')
        with col2:
            if st.button("삭제", key=f'delete_{task}', type="primary"):
                remove_task(task)
                st.session_state.toast_remove = task
                st.rerun()

    st.subheader("")

    # 할 일 추가
    st.subheader("할 일 추가")
    repetitions = ["매일 반복", "특정 요일마다 반복", "며칠마다 반복", "반복하지 않음"]
    repetition_type = st.selectbox("얼마나 반복할 건가요?", repetitions)

    # 매일 반복
    if repetition_type == "매일 반복":

        new_task_name = st.text_input("무슨 일을 해야 하나요?")

        col1, col2 = st.columns([4, 1])
        with col1:
            pass
        with col2:
            add_new_task = st.button("✚ 할 일 추가", type="primary")
        if add_new_task:
            if new_task_name:
                if save_task(new_task_name, "daily_tasks") == False:
                    st.error("이미 있는 할 일입니다!")
                else:
                    st.session_state.toast_add = new_task_name
                    st.rerun()
            else:
                st.error("할 일을 적어주세요!")