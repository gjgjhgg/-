import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민이 있나요? gemini-2.5-flash-lite가 진심 어린 조언을 해드려요.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 설정을 확인해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 당신의 연애 고민을 들어드릴 상담사입니다. 어떤 고민이 있으신가요? (예: 썸남/썸녀 심리가 궁금해요, 권태기인 것 같아요 등)"
        }
    ]

# 4. 기존 대화 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 이야기해주세요..."):
    
    # 사용자 메시지 추가 및 화면 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 6. AI 챗봇 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 페르소나 부여를 위한 시스템 지침(System Instruction) 설정
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction="당신은 공감 능력이 뛰어나면서도 때로는 현실적인 조언을 건네는 전문 연애 상담사입니다. 친구처럼 친근한 말투(해요체)를 사용하고, 사용자의 감정에 먼저 공감해준 뒤 구체적인 솔루션을 제안해주세요."
            )
            
            # Gemini 대화 형식에 맞게 이전 기록 변환 (user, model 형태)
            chat_history = []
            for msg in st.session_state.messages[:-1]: # 방금 넣은 사용자 입력 제외한 기록
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # 대화 시작 및 답변 생성
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_input)
            
            # 결과 출력 및 세션 저장
            ai_response = response.text
            message_placeholder.write(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            error_msg = f"죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다. (오류 내용: {str(e)})"
            message_placeholder.write(error_msg)
            # 오류 메시지는 세션 기록에 저장하지 않음
