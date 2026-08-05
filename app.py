import streamlit as st
import json
from datetime import datetime, timedelta, date

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
    task_names = [task["name"] for task in tasks]
    if name in task_names:
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

# 넣은 날짜를 현재 날짜와 비교해서 한글로 자연스럽게 바꿔주는 함수
def format_date(dt):
    days = (dt - st.session_state.today).days
    if days == 0:
        return "오늘"
    elif days == 1:
        return "내일"
    elif days == 2:
        return "모레"
    elif days == -1:
        return "어제"
    elif 3 <= days <= 14:
        return f'{days}일 후'
    elif -2 >= days >= -14:
        return f'{days}일 전'
    else:
        return f'{dt.year}년 {dt.month}월 {dt.day}일'

# 얼마나 반복하는지를 자연스럽게 한글로 바꿔주는 함수
def format_days(int, unit):
    unit_to_ko = {"day":"일", "week":"주"}
    if unit in unit_to_ko:
        if int == 1:
            return f'매{unit_to_ko[unit]}'
        else:
            return f'{int}{unit_to_ko[unit]}마다'
    else:
        if int == 1:
            return '매월'
        else:
            return f'{int}개월마다'

# ---------------------------------------------------------------------
# stage HOME

if st.session_state.stage == "HOME":

    st.subheader("오늘 할 일")

    # 오늘 할 일 계산하기
    today_tasks = []
    for t in tasks:
        start_date = datetime.strptime(
            t["start_date"], "%Y-%m-%d"
        ).date()
        days = (st.session_state.today - start_date).days
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
        formated_start_date = format_date(date.fromisoformat(task["start_date"]))
        if task["repeat_unit"] == None:
            if any(c.isdigit() for c in formated_start_date):
                formated_start_date = formated_start_date + '에'
            task_repeat_messages[task["name"]] = f'{formated_start_date} 표시, 반복되지 않음'
        else:
            task_repeat_messages[task["name"]] = (
                f'{formated_start_date}부터, {format_days(task["interval"], task["repeat_unit"])} 반복'
            )

    # 할 일 표시와 삭제 버튼
    for task in task_names:
        col1, col2, = st.columns([10, 1])
        with col1:
            st.checkbox(f'**{task}** -- *{task_repeat_messages[task]}*')
        with col2:
            if st.button("삭제", key=f'delete_{task}', type="primary"):
                remove_task(task)
                st.session_state.toast_remove = task
                st.rerun()

    st.subheader("")

    # 할 일 추가
    st.subheader("할 일 추가")

    new_name = st.text_input("무슨 일을 해야 하나요?")
    new_start_date = st.date_input(
        "언제부터 일정을 시작하나요?", st.session_state.today + timedelta(days=1), format="YYYY.MM.DD"
    )

    st.write("") # 간격 띄우기
    repetitions = ["반복 안 함", "_일마다 반복", "_주마다 반복", "_개월마다 반복"]
    repetition_type = st.selectbox("얼마나 반복할 건가요?", repetitions, index=0)

    if repetition_type == "반복 안 함":
        st.write("[!] 반복이 되지 않습니다")
        new_to_do = [new_name, None, None, new_start_date.isoformat()]

    elif repetition_type == "_일마다 반복":
        new_interval = st.number_input("며칠마다 반복하나요?", min_value=1)
        st.write(f'[!] {format_days(new_interval, "day")} 반복됩니다')
        new_to_do = [new_name, "day", new_interval, new_start_date.isoformat()]

    col1, col2 = st.columns([4, 1])
    with col1:
        pass
    with col2:
        add_new_task = st.button("✚ 할 일 추가", type="primary")
    if add_new_task:
        if new_name:
            if save_task(*new_to_do) == False:
                st.error("이미 있는 할 일입니다!")
            else:
                st.session_state.toast_add = new_name
                st.rerun()
        else:
            st.error("할 일을 적어주세요!")