# ───── 누적 피해 풀 & 확산 속도 ─────
total_potential_pool = int(my_followers * (1 + (friends_followers * 0.4)))
calculated_speed = story_count * (1 + (friends_followers * 0.01))

# ───── ⭐ 시각화 공 개수 계산 (0~100 구간은 1:1 매핑) ⭐ ─────
def map_followers(val, threshold=100, slider_max=1000, max_extra=50):
    """
    val ≤ threshold  → 1:1 매핑 (정확히 그 숫자만큼)
    val > threshold  → threshold~(threshold+max_extra) 범위로 압축
    """
    if val <= threshold:
        return val
    else:
        ratio = (val - threshold) / (slider_max - threshold)
        return threshold + int(ratio * max_extra)

# 내 팔로워: 0~100 → 0~100개 (1:1), 100~1000 → 100~150개로 압축
visual_my       = map_followers(my_followers,      threshold=100, slider_max=1000, max_extra=50)
# 친구 팔로워: 0~100 → 0~100개 (1:1), 100~500 → 100~150개로 압축
visual_extended = map_followers(friends_followers, threshold=100, slider_max=500,  max_extra=50)

# 총합 (최소 1개, 최대 250개로 성능 보호)
VISUAL_USERS = max(1, min(250, visual_my + visual_extended))

# ───── 사이드바 안내 ─────
st.sidebar.markdown("---")
st.sidebar.metric(
    label="🎯 현재 시뮬레이션 공 개수",
    value=f"{VISUAL_USERS}개",
    help="0~100명까지는 1:1로 정확히 매핑되며, 그 이상은 화면 가독성을 위해 압축됩니다."
)

# 1:1 매핑 여부 표시
exact_my       = "✅ 1:1" if my_followers      <= 100 else "📦 압축"
exact_extended = "✅ 1:1" if friends_followers <= 100 else "📦 압축"

st.sidebar.caption(
    f"• 내 직접 영향권: **{visual_my}명** ({exact_my})\n\n"
    f"• 친구의 친구까지: **+{visual_extended}명** ({exact_extended})\n\n"
    f"• 누적 피해 규모(수치): **{total_potential_pool:,}명**"
)
