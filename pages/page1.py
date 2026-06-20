import streamlit as st
import requests

st.markdown("---")
st.header("📝 [활동지] 정보 확산 분석 및 윤리적 실천 다짐")

# ✅ 구글 폼 정보
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeeEazvp_aUDB0T2Syaab1JrxayUt_ltVU2b_1lONbwKsXT8A/formResponse"
ENTRY_CLASS    = "entry.1744528295"   # 반
ENTRY_NUM      = "entry.973302941"    # 번호
ENTRY_NAME     = "entry.560543267"    # 이름
ENTRY_ANALYSIS = "entry.1308568821"   # 분석
ENTRY_PROMISE  = "entry.867457307"    # 다짐
ENTRY_ACTION   = "entry.553841103"    # 실천

with st.form("student_feedback_form"):
    col1, col2, col3 = st.columns(3)
    c_class = col1.selectbox("반", [f"{i}" for i in range(1, 11)])      # 1~10반
    c_num   = col2.selectbox("번호", [f"{i}" for i in range(1, 34)])    # 1~33번
    c_name  = col3.text_input("이름")

    analysis    = st.text_area("1. 시뮬레이션 관찰 및 데이터 해석")
    promise     = st.text_area("2. 디지털 정보 윤리에 대한 나의 다짐")
    action_plan = st.text_area("3. 향후 실천할 구체적인 행동 수칙")

    submitted = st.form_submit_button("학습지 제출하기")

    if submitted:
        if not c_name.strip():
            st.error("이름을 입력해주세요.")
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
                r = requests.post(
                    GOOGLE_FORM_URL,
                    data=payload,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if r.status_code in (200, 302):
                    st.success(f"✅ {c_class} {c_num} {c_name} 학생, 제출 완료되었습니다!")
                else:
                    st.error(f"제출 실패 (상태코드 {r.status_code})")
            except Exception as e:
                st.error(f"전송 오류: {e}")

st.info("💡 제출 시 선생님의 구글 스프레드시트로 자동 취합됩니다.")
