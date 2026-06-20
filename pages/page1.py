import streamlit as st
import urllib.parse
import requests

st.markdown("---")
st.header("📝 [활동지] 정보 확산 분석 및 윤리적 실천 다짐")

# 👇 본인 구글 폼의 formResponse URL과 entry ID로 교체
GOOGLE_FORM_URL = "https://docs.google.com/spreadsheets/d/1O8VwyjNp08xU_H-JcMBFSBtXBJRn3-sOB-jCESBKsM0/edit?usp=sharing"
ENTRY_CLASS    = "entry.1111111111"
ENTRY_NUM      = "entry.2222222222"
ENTRY_NAME     = "entry.3333333333"
ENTRY_ANALYSIS = "entry.4444444444"
ENTRY_PROMISE  = "entry.5555555555"
ENTRY_ACTION   = "entry.6666666666"

with st.form("student_feedback_form"):
    col1, col2, col3 = st.columns(3)
    c_class = col1.text_input("반")
    c_num   = col2.text_input("번호")
    c_name  = col3.text_input("이름")

    analysis    = st.text_area("1. 시뮬레이션 관찰 및 데이터 해석")
    promise     = st.text_area("2. 디지털 정보 윤리에 대한 나의 다짐")
    action_plan = st.text_area("3. 향후 실천할 구체적인 행동 수칙")

    submitted = st.form_submit_button("학습지 제출하기")

    if submitted:
        if not (c_name and c_class and c_num):
            st.error("반, 번호, 이름을 모두 입력해주세요.")
        else:
            payload = {
                ENTRY_CLASS:    c_class,
                ENTRY_NUM:      c_num,
                ENTRY_NAME:     c_name,
                ENTRY_ANALYSIS: analysis,
                ENTRY_PROMISE:  promise,
                ENTRY_ACTION:   action_plan,
            }
            try:
                r = requests.post(GOOGLE_FORM_URL, data=payload, timeout=10)
                # 구글 폼은 정상 제출 시 200 또는 302 반환
                if r.status_code in (200, 302):
                    st.success(f"{c_name} 학생, 제출 완료되었습니다!")
                else:
                    st.error(f"제출 실패 (상태코드 {r.status_code})")
            except Exception as e:
                st.error(f"전송 오류: {e}")

st.info("💡 제출 시 선생님의 구글 스프레드시트로 자동 취합됩니다.")
