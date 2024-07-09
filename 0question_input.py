# streamlit run 0question_input.py
# 질문 입력 페이지

# 라이브러리
import streamlit as st
from openai import OpenAI
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 사이드바 생성 
# 사이드바에서 사용자 api키, 구글 인증, thread 아이디 입력할 수 있도록 하고자 함.
with st.sidebar:
# openai API 키 입력
    openai_api_key = st.text_input("sk-proj-2tY5WiQt2AOREVKz2zpeT3BlbkFJB5HQk9p8iQUHVa5SIsFz")
    if openai_api_key:

# 글로벌 함수로 api키 등록
        st.session_state['usingapikey'] = openai_api_key
        client = OpenAI(api_key=st.session_state['usingapikey'])

# thread 생성
        new_thread = client.beta.threads.create()
        st.caption("처음 한 번만 thread를 복사하여 사용하세요.")
        st.write(new_thread.id)

# 클라이언트 생성
# openai_api_key='sk-proj-2tY5WiQt2AOREVKz2zpeT3BlbkFJB5HQk9p8iQUHVa5SIsFz'
# client = OpenAI(api_key=openai_api_key)
assistant_id = 'asst_f7UDR07vZ7WK1rQNMKvhiBVN'

# 홈페이지 구성 
st.subheader('초등학교 사회 5학년 2학기 서술형 평가 연습 도구')

# 사용 방법 소개
with st.container(border=True):
    st.write(
"""
<사용 방법>

1. 왼쪽에 나온 thread_id를 복사하여 아래 입력 창에 입력해주세요.
    
2. [추가 자료 입력]에서 평가에 활용할 추가 자료를 입력합니다. 수업 시간에 활용한 수업자료나 활동지를 pdf로 변환하여 업로드합니다.

3. [평가 문항 입력]에서 평가 문항과 모범 답안을 입력합니다. 평가 문항은 최대 3개 입력할 수 있습니다.

4. [주의사항 입력]에서 채점 및 피드백에 대해 설정하고 싶은 내용을 입력합니다.

5. [학생 답안 입력]에서 학생 답안을 입력하세요. '답안 입력' > '채점 및 피드백 생성' > '저장' 버튼을 차례대로 진행합니다.
""")
   
# thread 입력
usingthread = st.text_input("thread를 입력해주세요.")
thread_id = usingthread

# 글로벌 함수로 thread 아이디 등록
st.session_state['usingthread'] = usingthread

# 탭설정
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. 단원 선택", "2. 추가 자료 입력", "3. 평가 문항 입력", "4. 주의사항 입력", "5. 학생 답안 입력"])

# 탭1: 단원 선택
# 단원에 따라 assistant ID 변경(미리 입력한 파일이 다름. 이유는 가볍게 만들기 위해, 아래 어시스턴트 아이디 다르게 해야함.)
with tab1:
    st.subheader("1. 단원 선택")
    chapter_select = st.selectbox
    st.selectbox("",("1-1 나라의 등장과 발전","1-2 독창적 문화를 발전시킨 고려", "1-3 민족 문화를 지켜 나간 조선"), index=None, placeholder="단원을 선택해주세요.")
    if chapter_select == "1-1 나라의 등장과 발전":
        assistant_id = assistant_id

    elif chapter_select == "1-2 독창적 문화를 발전시킨 고려":
        assistant_id = assistant_id

    elif chapter_select == "1-3 민족 문화를 지켜 나간 조선":
        assistant_id = assistant_id

# 탭2: 추가 자료 입력
with tab2:
    st.header("2. 추가 자료 입력")

# 파일 업로더 입력
    uploaded_file = st.file_uploader("")

# 파일이 선택되어 있고 업로드 버튼을 누르면 파일 업로드 
    run_file_button = st.button('파일 업로드') 

    if uploaded_file is not None and run_file_button:
        uploaded_file_response = client.files.create(
        file=uploaded_file, 
        purpose="assistants"
        )

# 생성된 파일 id를 vector stores에 입력하는 과정
        vector_store_file = client.beta.vector_stores.files.create(
        vector_store_id='vs_fdybgnMcS5HCdNQCYDiwxBbe',
        file_id=uploaded_file_response.id
        )
        st.success(f'파일이 성공적으로 등록되었습니다.')
    
# 업로드된 파일 목록 표시
    filelist = st.checkbox("업로드된 파일 목록")
    if filelist:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='현재 업로드된 파일 목록을 모두 보여주세요. 파일 목록 외에 아무 문장도 넣지 마세요. 파일 목록 번호는 1번부터 시작하세요.',
        )

        run = client.beta.threads.runs.create(
        thread_id=st.session_state['usingthread'],
        assistant_id=assistant_id
        )
        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        thread_messages = client.beta.threads.messages.list(st.session_state['usingthread'])
        msg = thread_messages.data[0].content[0].text.value
        st.write(msg)

# 탭3: 문항 입력
with tab3:
    st.header("3. 평가 문항 입력")

    col1, col2 = st.columns(2)

    with col1:
        question1 = st.text_area("1번 문항")
        st.divider()

        question2 = st.text_area("2번 문항")
        st.divider()

        question3 = st.text_area("3번 문항")
        st.divider()

    with col2:    
        correctanswer1 = st.text_area("1번 모범답안")
        st.divider()

        correctanswer2 = st.text_area("2번 모범답안")
        st.divider()

        correctanswer3 = st.text_area("3번 모범답안")
        st.divider()

#평가 문항 입력
    question_input_button = st.button('문항 입력')

    if question_input_button:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='1번 문항은 <' + question1 + '> 입니다. 사용자가 입력한 모범답안은 <' + correctanswer1 + 
        ' 입니다. 2번 문항은 <' + question2 + '> 입니다. 사용자가 입력한 모범답안은 <' + correctanswer2 + 
        ' 입니다. 3번 문항은 <' + question3 +'> 입니다. 사용자가 입력한 모범답안은 <' + correctanswer3 + ' 입니다. '
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state['usingthread'],
            assistant_id=assistant_id
            )

        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)
        st.success(f'서술형 문항이 성공적으로 등록되었습니다.')

# 서술형 평가 문항 및 모범답안 확인
    questioncorrectanswerlist = st.checkbox("서술형 평가 문항 및 모범답안 확인")
    if questioncorrectanswerlist:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='현재 업로드된 서술형 평가 문항과 모범답안을 모두 보여주세요. 표 형태로 보여주세요. 반드시 서술형 평가 문항와 모범답안 외에 다른 문장을 넣지 마세요.',
        )

        run = client.beta.threads.runs.create(
        thread_id=st.session_state['usingthread'],
        assistant_id=assistant_id
        )
        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        thread_messages = client.beta.threads.messages.list(st.session_state['usingthread'])
        msg = thread_messages.data[0].content[0].text.value
        st.write(msg)

# 탭4: 평가 주의사항 입력
with tab4:
    st.header("4. 평가 주의사항 입력")
    feedbackinstruction = st.text_area("평가 주의사항")
    st.divider()

    feedbackinstruction_input_button = st.button('평가 주의사항 입력')

    if feedbackinstruction_input_button:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='평가 주의사항은 <' + feedbackinstruction + '> 입니다. 피드백을 제공할 때 위 내용을 고려해서 작성해주시기 바랍니다.'
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state['usingthread'],
            assistant_id=assistant_id
            )

        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        st.success(f'평가 주의사항이 입력되었습니다.')

# 평가 주의사항 확인
    guidelinelist = st.checkbox("평가 주의사항 확인")
    if guidelinelist:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='현재 업로드된 평가 주의사항을 모두 보여주세요. 반드시 평가 주의사항 외에 다른 문장을 넣지 마세요.',
        )

        run = client.beta.threads.runs.create(
        thread_id=st.session_state['usingthread'],
        assistant_id=assistant_id
        )
        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        thread_messages = client.beta.threads.messages.list(st.session_state['usingthread'])
        msg = thread_messages.data[0].content[0].text.value
        st.write(msg)

# 탭5: 학생 답안 입력
with tab5:
    st.subheader("5. 학생 답안 입력")

# 문항 보이기
    questionlist = st.checkbox("서술형 문항을 확인하세요.")
    if questionlist:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='등록된 평가 문항을 보여주세요. 반드시 평가 문항 외에 다른 문장을 넣지 마세요.',
        )

        run = client.beta.threads.runs.create(
        thread_id=st.session_state['usingthread'],
        assistant_id=assistant_id
        )
        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        thread_messages = client.beta.threads.messages.list(st.session_state['usingthread'])
        msg = thread_messages.data[0].content[0].text.value
        st.write(msg)

# 학생 답안 입력
    answer1 = st.text_area("1번 답안")
    st.divider()

    answer2 = st.text_area("2번 답안")
    st.divider()

    answer3 = st.text_area("3번 답안")
    st.divider()

    answer_input_button = st.button('답안 입력')

    if answer_input_button:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='1번 문항에 대한 답안은 <' + answer1 + 
        '> 입니다. 2번 문항에 대한 답안은 <' + answer2 + 
        '> 입니다. 3번 문항에 대한 답안은 <' + answer3 +'> 입니다.'
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state['usingthread'],
            assistant_id=assistant_id
            )

        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run_id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        st.success(f'학생 답안이 성공적으로 등록되었습니다.')

# 채점 및 피드백 생성
    feedback_output_button = st.button('채점 및 피드백 생성')

    if feedback_output_button:
        thread_message = client.beta.threads.messages.create(
        thread_id=st.session_state['usingthread'],
        role="user",
        content='학생 입력 답안에 대한 채점 및 피드백을 생성해주세요. instructions와 입력된 평가 주의사항에 따라 채점 및 피드백을 진행해주세요.'
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state['usingthread'],
            assistant_id=assistant_id
        )

        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['usingthread'],
                run_id=run.id
                )   
            if run.status == "completed":
                break
            else:
                time.sleep(2)

        thread_messages = client.beta.threads.messages.list(st.session_state['usingthread'])
        st.session_state['feedback'] = thread_messages.data[0].content[0].text.value
        st.write(st.session_state['feedback'])

# 자동 저장 기능
    saveresult = st.button("저장 버튼")

    if saveresult and 'feedback' in st.session_state:

    # 구글 시트 열기
        # Google Sheets 인증 설정
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name('C:\streamlit/240509/m20223715-57735b2cc43e.json', scope)
        gc = gspread.authorize(credentials)

        # 스프레드시트 열기
        spreadsheet = gc.open('abc')
        worksheet = spreadsheet.sheet1  # 첫 번째 시트 선택

        # 저장하기
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([current_time, answer1, answer2, answer3, st.session_state['feedback']])
        st.success(f'피드백이 성공적으로 Google Sheets에 저장되었습니다.')