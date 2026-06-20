import streamlit as st
import requests

st.markdown("---")
st.header("📝 [활동지] 정보 확산 분석 및 윤리적 실천 다짐")

# ✅ 구글 폼 정보
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeeEazvp_aUDB0T2Syaab1JrxayUt_ltVU2b_1lONbwKsXT8A/formResponse"
ENTRY_CLASS    = "entry.1744528295"
ENTRY_NUM      = "entry.973302941"
ENTRY_NAME     = "entry.560543267"
ENTRY_ANALYSIS = "entry.1308568821"
ENTRY_PROMISE  = "entry.867457307"
ENTRY_ACTION   = "entry.553841103"

with st.form("student_feedback_form"):
    # ───── 학생 정보 ─────
    col1, col2, col3 = st.columns([1, 1, 2])
    c_class = col1.selectbox("반", [f"{i}반" for i in range(1, 11)])
    c_num   = col2.selectbox("번호", [f"{i}번" for i in range(1, 34)])
    c_name  = col3.text_input("이름")

    st.markdown("---")

    # ───── 질문 1 ─────
    st.subheader("질문 1. 데이터 해석: 왜 내 팔로워보다 훨씬 더 많은 사람에게 퍼질까?")
    st.markdown(
        "내가 올린 글을 내 친구들이 보고, 그 친구들의 친구들까지 보게 되면서 "
        "정보가 퍼지는 속도가 빨라졌나요?\n\n"
        "단순히 '내 팔로워'만 글을 볼 때와 '내 친구들의 팔로워'까지 "
        "글이 퍼질 때, 그래프의 모양이 어떻게 다른지(얼마나 빨리 올라가는지) "
        "여러분이 직접 관찰한 내용을 바탕으로 써보세요."
    )
    analysis = st.text_area(
        "✍️ 나의 관찰 및 데이터 해석",
        placeholder="예) 처음에는 천천히 늘다가, 친구의 친구까지 퍼지는 순간부터 그래프가 갑자기 솟구쳐 올랐다...",
        height=130,
        key="q1",
    )

    st.markdown("---")

    # ───── 질문 2 ─────
    st.subheader("질문 2. 비판적 사고: 정보의 '속도'는 왜 위험할까?")
    st.markdown(
        "시뮬레이터에서 빨간색 공(정보가 퍼진 사람)들이 점점 늘어나는 모습을 보았죠?\n\n"
        "만약 이게 내가 실수로 올린 '친구의 비밀'이나 '잘못된 정보'라면, "
        "이렇게 순식간에 퍼지는 정보가 나중에 지우고 싶어도 지우기 어려운 이유는 "
        "무엇일까요?\n\n"
        "💭 디지털 성범죄, 학교 폭력, 가짜 뉴스 같은 구체적인 사례를 떠올려보세요."
    )
    promise = st.text_area(
        "✍️ 나의 비판적 사고",
        placeholder="예) 한 번 퍼진 정보는 여러 사람의 휴대폰에 저장되기 때문에...",
        height=130,
        key="q2",
    )

    st.markdown("---")

    # ───── 질문 3 ─────
    st.subheader("질문 3. 윤리적 실천: 네트워크 속 '나'의 책임")
    st.markdown(
        "내가 무심코 누른 '좋아요'나 '게시물, 스토리 등 공유'가 시뮬레이션 그래프처럼 "
        "순식간에 수많은 사람에게 전파될 수 있다는 사실을 알게 되었습니다.\n\n"
        "앞으로 SNS에 게시물을 올리거나 공유하기 전, "
        "떠올려야 할 생각과 지켜야할 행동 규칙을 "
        "만들어 봅시다. 어떤 규칙을 만들고 싶나요? 3가지 이상 작성하세요."
    )
    action_plan = st.text_area(
        "✍️ 나의 디지털 시민 다짐 규칙",
        placeholder="예) 공유 버튼을 누르기 전, ①출처가 확실한가 ②누가 상처받지 않는가 ③나중에 후회하지 않는가를 3초간 생각한다.",
        height=130,
        key="q3",
    )

    st.markdown("---")
    submitted = st.form_submit_button("📨 보고서 제출하기", use_container_width=True)

    if submitted:
        if not c_name.strip():
            st.error("이름을 입력해주세요.")
        elif not (analysis.strip() and promise.strip() and action_plan.strip()):
            st.error("세 가지 질문에 모두 답변해 주세요.")
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
                    st.success(f"✅ {c_class} {c_num} {c_name} 학생, 제출 완료되었습니다! 수고했어요 👏")
                    st.balloons()
                else:
                    st.error(f"제출 실패 (상태코드 {r.status_code})")
            except Exception as e:
                st.error(f"전송 오류: {e}")

st.info("💡 제출 시 선생님의 구글 스프레드시트로 자동 취합됩니다.")
