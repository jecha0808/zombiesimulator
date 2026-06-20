import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 페이지 설정
st.set_page_config(page_title="디지털 정보 확산 시뮬레이터", page_icon="🧟", layout="wide")

st.title("🧟 정보 중요도에 따른 디지털 전파 시뮬레이터")
st.markdown("""
교과서 225쪽의 **'디지털 공간에서 정보의 확산'**을 시각적으로 체험하는 앱입니다. 
왼쪽 사이드바에서 **정보의 중요도와 자극성**을 조절해 보세요. 정보의 성격에 따라 얼마나 전파 속도가 빨라지는지 3D 화면으로 확인할 수 있습니다!
""")

st.markdown("---")

# 2. 사이드바 - 제어 파라미터 (학생 조작 포인트)
st.sidebar.header("⚙️ 디지털 정보 속성 설정")

# [수업 포인트] 정보의 자극성이 높을수록 이동 속도(SPEED)에 가중치가 붙음
info_type = st.sidebar.selectbox(
    "1. 유포되는 정보의 종류 선택",
    ["일반적인 일상 글 (자극성 낮음)", "반짝 유행하는 밈/트렌드 (자극성 보통)", "중요한 비밀 및 자극적인 루머 (자극성 매우 높음)"]
)

if "낮음" in info_type:
    speed_weight = 4
    radius_weight = 0.6
    bg_color = "#e2e8f0" # 회색 배경
elif "보통" in info_type:
    speed_weight = 8
    radius_weight = 1.0
    bg_color = "#fef08a" # 노란색 배경
else:
    speed_weight = 16
    radius_weight = 1.6
    bg_color = "#fca5a5" # 빨간색 배경

# 인구 밀도 조절 슬라이더
num_people = st.sidebar.slider("2. 네트워크 안의 유저 수 (명)", min_value=10, max_value=60, value=30, step=5)

# 3. 메인 화면 레이아웃 분할
col_sim, col_guide = st.columns([1.3, 0.7])

with col_sim:
    st.subheader("🎮 3D 네트워크 확산 가상 공간 (Web VPython)")
    
    # 스트림릿 슬라이더 값들을 VPython 자바스크립트 코드로 동적 주입하기 위한 HTML/JS 소스
    vpython_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://www.glowscript.org/package/glowscript.2.9.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    </head>
    <body>
    <div id="glowscript" class="glowscript"></div>
    <script>
    window.__context = {{
        glowscript_container: $("#glowscript")
    }};
    
    scene = canvas({{width: 650, height: 450, center: vec(0,0,0)}});
    var L = 20;
    box({{pos: vec(0,0,0), size: vec(L*2, L*2, 1), color: color.gray(0.2), opacity: 0.2}});
    
    var NUM_PEOPLE = {num_people};
    var SPEED = {speed_weight};
    var INFECTION_RADIUS = {radius_weight};
    
    var people = [];
    var dt = 0.05;
    var time_elapsed = 0;
    
    // 최초 좀비 숙주 생성
    var zombie = sphere({{pos: vec(random()*L*2-L, random()*L*2-L, 0), radius: 0.6, color: color.red, make_trail: true, trail_radius: 0.1}});
    zombie.status = "ZOMBIE";
    zombie.vel = vec(random()*2-1, random()*2-1, 0).norm().multiply(SPEED);
    people.push(zombie);
    
    # 일반 사람 생성
    for(var i=0; i<NUM_PEOPLE-1; i++) {{
        var p = sphere({{pos: vec(random()*L*2-L, random()*L*2-L, 0), radius: 0.4, color: color.green}});
        p.status = "HUMAN";
        p.vel = vec(random()*2-1, random()*2-1, 0).norm().multiply(SPEED);
        people.push(p);
    }}
    
    var label_info = label({{pos: vec(0, L+3, 0), text: "시뮬레이션 중...", height: 14}});
    
    // 메인 애니메이션 루프
    function mainLoop() {{
        time_elapsed += dt;
        var num_zombies = 0;
        
        for(var i=0; i<people.length; i++) {{
            if(people[i].status == "ZOMBIE") num_zombies++;
        }}
        
        label_info.text = "시간: " + time_elapsed.toFixed(1) + "초 | 🔴 감염 유저: " + num_zombies + "명 / " + NUM_PEOPLE + "명";
        
        // 이동 및 벽 충돌
        for(var i=0; i<people.length; i++) {{
            var p = people[i];
            p.pos = p.pos.add(p.vel.multiply(dt));
            
            if(Math.abs(p.pos.x) > L) {{ p.vel.x = -p.vel.x; p.pos.x = p.pos.x > 0 ? L : -L; }}
            if(Math.abs(p.pos.y) > L) {{ p.vel.y = -p.vel.y; p.pos.y = p.pos.y > 0 ? L : -L; }}
        }}
        
        // 감염 충돌 검사
        for(var i=0; i<people.length; i++) {{
            for(var j=i+1; j<people.length; j++) {{
                var p1 = people[i];
                var p2 = people[j];
                if((p1.status == "ZOMBIE" && p2.status == "HUMAN") || (p1.status == "HUMAN" && p2.status == "ZOMBIE")) {{
                    if(p1.pos.sub(p2.pos).mag < INFECTION_RADIUS) {{
                        p1.status = "ZOMBIE"; p1.color = color.red;
                        p2.status = "ZOMBIE"; p2.color = color.red;
                    }}
                }}
            }}
        }}
        
        if(num_zombies < NUM_PEOPLE) {{
            setTimeout(mainLoop, 30);
        }} else {{
            label_info.text = "🚨 전원 전파 완료! 총 걸린 시간: " + time_elapsed.toFixed(1) + "초";
        }}
    }}
    
    setTimeout(mainLoop, 500);
    </script>
    </body>
    </html>
    """
    
    # 스트림릿 내부에 VPython 스크립트 실행 화면 임베딩
    components.html(vpython_code, height=520, scrolling=False)

with col_guide:
    st.subheader("💡 현재 정보 속성 리포트")
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {bg_color}; color: #1e293b; font-weight: bold;">
        📊 선택한 정보: {info_type}<br>
        🚀 전파 속도 가중치: {speed_weight}배 빠른 전송<br>
        🎯 관심 및 공유 반경: {radius_weight} 픽셀 이내 접촉 시 전파
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🧑‍🏫 수업용 탐구 활동 가이드
    1. **일상적인 글**을 올렸을 때 전체 네트워크로 퍼지는 시간을 우측 상단 타이머로 기록해 보세요.
    2. **자극적인 루머**로 변경했을 때, 3D 공간 속 구체들의 **꼬리(Trail)와 속도**가 어떻게 변하는지 관찰해 보세요.
    3. **결론 도출**: "중요하고 자극적인 정보일수록 사람들이 더 빠르게 퍼다 나르고(속도 증가), 더 넓은 네트워크로 공유(반경 증가)하여 순식간에 디지털 공간 전체로 퍼져나간다는 점"을 토의해 봅시다.
    """)
