import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 시뮬레이션] 내 개인정보가 좀비처럼 퍼진다면?")
st.markdown("""
교과서 225쪽의 **'디지털 공간에서 정보의 확산 속도 체험하기'** 단원을 위한 융합 실습 앱입니다.  
왼쪽 사이드바에서 **SNS 공유 빈도(속도)**를 조절해 보세요. 정보의 확산 속도가 숫자에 따라 얼마나 폭발적으로 변하는지 3D 화면으로 확인할 수 있습니다.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성 (학생 조작 포인트)
st.sidebar.header("⚙️ 시뮬레이션 환경 제어")

# 학생들이 직접 수정해 볼 수 있는 전역 설정 변수들
sharing_speed = st.sidebar.slider(
    "1. SNS 공유 빈도 (공들의 속도)", 
    min_value=1, 
    max_value=15, 
    value=5, 
    step=1
)

num_users = st.sidebar.number_input(
    "2. 전체 가상 SNS 사용자 수 (명)", 
    min_value=10, 
    max_value=60, 
    value=40, 
    step=5
)

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 범례 가이드**
* ⚪ **하얀 공**: 안전한 일반 SNS 사용자
* 🔴 **빨간 공**: 개인정보 유출 피해자
* 🖱️ 3D 화면을 마우스 드래그로 회전하거나, 마우스 휠로 확대/축소할 수 있습니다.
""")

# 3. 레이아웃 분할 (좌측: 3D 시뮬레이터 / 우측: 탐구 리포트 및 발문)
col_sim, col_guide = st.columns([1.3, 0.7])

with col_sim:
    st.subheader("🎮 3D 네트워크 확산 가상 공간 (Web VPython)")
    
    # 스트림릿의 입력값을 자바스크립트 엔진으로 전달하여 Web VPython(GlowScript) 가동
    vpython_embed_code = f"""
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
    
    // 3차원 캔버스 설정
    scene = canvas({{width: 650, height: 500, center: vec(0,0,0)}});
    scene.background = color.gray(0.1);
    
    var CONTAINER_SIZE = 20;
    var NUM_USERS = {num_users};
    var BALL_RADIUS = 0.6;
    var sharing_speed = {sharing_speed};
    
    // 투명한 3D 상자 테두리 생성
    box({{pos: vec(0,0,0), size: vec(CONTAINER_SIZE*2, CONTAINER_SIZE*2, CONTAINER_SIZE*2), opacity: 0.1, color: color.white}});
    
    var users = [];
    var time_elapsed = 0;
    var infected_count = 1;
    var dt = 0.05;
    
    // 객체 초기 생성 및 3차원 랜덤 배치
    for(var i=0; i<NUM_USERS; i++) {{
        var rx = (Math.random() * (CONTAINER_SIZE*2 - 4)) - (CONTAINER_SIZE - 2);
        var ry = (Math.random() * (CONTAINER_SIZE*2 - 4)) - (CONTAINER_SIZE - 2);
        var rz = (Math.random() * (CONTAINER_SIZE*2 - 4)) - (CONTAINER_SIZE - 2);
        
        var u_color = (i == 0) ? color.red : color.white;
        var u_infected = (i == 0) ? true : false;
        
        var user = sphere({{pos: vec(rx, ry, rz), radius: BALL_RADIUS, color: u_color}});
        
        // 3차원 랜덤 방향 벡터 설정
        var vx = (Math.random() * 2) - 1;
        var vy = (Math.random() * 2) - 1;
        var vz = (Math.random() * 2) - 1;
        user.velocity = vec(vx, vy, vz).norm();
        user.infected = u_infected;
        
        users.push(user);
    }}
    
    var label_info = label({{pos: vec(0, CONTAINER_SIZE + 3, 0), text: "준비 중...", height: 14}});
    
    // 메인 시뮬레이션 프레임 연산 루프
    function runSimulation() {{
        if (infected_count < NUM_USERS) {{
            time_elapsed += dt;
        }}
        
        label_info.text = "⏳ 걸린 시간: " + time_elapsed.toFixed(1) + "초 | 🔴 감염 계정: " + infected_count + " / " + NUM_USERS + "개";
        
        // 1. 3D 이동 및 공간 벽면 충돌 처리
        for(var i=0; i<users.length; i++) {{
            var user = users[i];
            user.pos = user.pos.add(user.velocity.multiply(sharing_speed * dt));
            
            // X, Y, Z축 경계면 반사 처리
            if(Math.abs(user.pos.x) >= CONTAINER_SIZE - BALL_RADIUS) {{
                user.velocity.x = -user.velocity.x;
                user.pos.x = user.pos.x > 0 ? (CONTAINER_SIZE - BALL_RADIUS) : -(CONTAINER_SIZE - BALL_RADIUS);
            }}
            if(Math.abs(user.pos.y) >= CONTAINER_SIZE - BALL_RADIUS) {{
                user.velocity.y = -user.velocity.y;
                user.pos.y = user.pos.y > 0 ? (CONTAINER_SIZE - BALL_RADIUS) : -(CONTAINER_SIZE - BALL_RADIUS);
            }}
            if(Math.abs(user.pos.z) >= CONTAINER_SIZE - BALL_RADIUS) {{
                user.velocity.z = -user.velocity.z;
                user.pos.z = user.pos.z > 0 ? (CONTAINER_SIZE - BALL_RADIUS) : -(CONTAINER_SIZE - BALL_RADIUS);
            }}
        }}
        
        // 2. 이중 반복문을 활용한 구체 간 3차원 충돌 감지 및 전파
        for(var i=0; i<users.length; i++) {{
            for(var j=i+1; j<users.length; j++) {{
                var u1 = users[i];
                var u2 = users[j];
                
                // 두 점 사이의 3차원 거리 계산
                var dist = u1.pos.sub(u2.pos).mag;
                
                if(dist < (BALL_RADIUS * 2)) {{
                    if(u1.infected && !u2.infected) {{
                        u2.color = color.red;
                        u2.infected = true;
                        infected_count++;
                    }} else if(u2.infected && !u1.infected) {{
                        u1.color = color.red;
                        u1.infected = true;
                        infected_count++;
                    }}
                }}
            }}
        }}
        
        // 루프 제어
        if(infected_count < NUM_USERS) {{
            setTimeout(runSimulation, 16); // 약 60fps에 맞추어 루프 실행
        }} else {{
            label_info.text = "🚨 전원 유출 완료! 총 확산 시간: " + time_elapsed.toFixed(1) + "초";
        }}
    }}
    
    // 스타트 딜레이 후 실행
    setTimeout(runSimulation, 300);
    </script>
    </body>
    </html>
    """
    
    # 스트림릿 컴포넌트로 3D 화면 띄우기
    components.html(vpython_embed_code, height=560, scrolling=False)

with col_guide:
    st.subheader("💡 수업용 탐구 활동 보고서")
    
    # 현재 적용된 설정을 카드 형태로 보기 좋게 시각화
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: #f1f5f9; color: #1e293b; border-left: 5px solid #ef4444; margin-bottom: 20px;">
        📌 <b>현재 네트워크 설정 데이터</b><br>
        • 설정된 공유 속도: <b>{sharing_speed}</b><br>
        • 참가자(노드) 밀도: <b>{num_users}명</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📝 학생 탐구 과제 (빈칸 채우기)
    왼쪽의 제어창 수치를 바꿔가며 아래 표를 완성하고 결론을 도출해 보세요.
    
    1. **공유 속도 변화에 따른 전원 유출 시간 측정**
       * 속도 `2` 일 때 걸린 시간: ( &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ) 초
       * 속도 `5` 일 때 걸린 시간: ( &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ) 초
       * 속도 `12` 일 때 걸린 시간: ( &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ) 초
    
    2. **생각 확장하기 질문 (발문)**
       * 사각형 교실(2D)에서 소문이 퍼지는 속도와 비교했을 때, 전 방향(3D)으로 연결된 디지털 공간의 확산 특징은 무엇인가요?
       * 단 한 번의 단톡방 유출이 왜 무서운지 시뮬레이션 속 **'빨간 공의 증가 곡선 유형'**을 바탕으로 설명해 봅시다.
    """)

    # 시뮬레이션 새로고침을 위한 스트림릿 내장 버튼
    if st.button("🔄 시뮬레이션 다시 시작하기"):
        st.rerun()
