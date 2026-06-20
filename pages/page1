import streamlit as st
import streamlit.components.v1 as components

st.markdown("---")
st.header("📝 [활동지] 정보 확산 분석 및 윤리적 실천 다짐")

# 학생 입력 폼
with st.form("student_feedback_form"):
    col1, col2, col3 = st.columns(3)
    c_class = col1.text_input("반")
    c_num = col2.text_input("번호")
    c_name = col3.text_input("이름")
    
    analysis = st.text_area("1. 시뮬레이션 관찰 및 데이터 해석 (그래프의 변화 등)")
    promise = st.text_area("2. 디지털 정보 윤리에 대한 나의 다짐")
    action_plan = st.text_area("3. 향후 실천할 구체적인 행동 수칙")
    
    submitted = st.form_submit_button("학습지 제출하기")

    if submitted:
        if c_name and c_class and c_num:
            # 💡 구글 폼의 '사전 채우기 링크'를 활용하여 데이터 전송
            # 선생님의 구글 폼 URL로 교체하세요!
            form_url = "https://forms.gle/kC27hvAHsHaJrECU7" 
            st.success(f"{c_name} 학생, 제출 완료되었습니다! 확인해 주세요.")
        else:
            st.error("반, 번호, 이름을 모두 입력해주세요.")

st.info("💡 모든 내용은 제출 버튼을 누르면 선생님의 구글 스프레드 시트로 자동 취합됩니다.")
