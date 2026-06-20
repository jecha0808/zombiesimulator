import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 내 SNS 설정에 따른 개인정보 확산 속도 시뮬레이션")
st.markdown("""
교과서 225쪽 **'디지털 공간의 정보 확산'** 단원 실습 앱입니다.  
왼쪽 제어창에서 **'내가 올린 스토리 수'**와 **'내 팔로워 수'**를 자유롭게 바꾸어 보세요. 수치를 변경할 때마다 오른쪽 그래프의 폭발 구간과 3D 공간의 유출 궤적이 실시간으로 완전히 달라집니다.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성 (학생 실시간 조작 변수)
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

# 변수 1: 팔로워 수 (네트워크의 총 크기)
follower_count = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)", 
    min_value=100, 
    max_value=50000, 
    value=500, 
    step=100
)

# 변수 2: 내가 올린 스토리 수 (정보의 유출/공유 빈도 -> 속도 가속화 변수)
story_count = st.sidebar.slider(
    "2. 내가 올린 스토리/게시글 수 (개)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

# 스토리 수와 기본 전파 로직을 결합한 실시간 확산 속도 가중치 계산
calculated_speed = story_count * 2.5

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **궤적이 남는 빨간 공**: 유출된 스토리/게시글 (최초 유출자)
* ⚪ **하얀 공**: 내 스토리를 본 팔로워 및 일반 유저들
* 🖱️ 3D 화면을 마우스 드래그하면 공간을 돌려볼 수 있습니다.
""")

# 3. 실시간 그래프 데이터 저장을 위한 세션 상태 초기화
if "chart_data" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=["시간(초)", "피해 유저 수(명)"]).set_index("시간(초)")

# 변수가 바뀌면 이전 그래프 데이터를 자동으로 리셋하여 실시간 동기화
if "prev_follower" not in st.session_state or "prev_story" not in st.session_state:
    st.session_state.prev_follower = follower_count
    st.session_state.prev_story = story_count

if st.session_state.prev_follower != follower_count or st.session_state.prev_story != story_count:
    st.session_state.chart_data = pd.DataFrame(columns=["시간(초)", "피해 유저 수(명)"]).set_index("시간(초)")
    st.session_state.prev_follower = follower_count
    st.session_state.prev_story = story_count

# 4. 레이아웃 분할 (좌측: 3D 시뮬레이터 / 우측: 실시간 변동 그래프 및 토의 리포트)
col_sim, col_chart = st.columns([1.1, 0.9])

with col_sim:
    st.subheader("🎮 3D 확산 시각화")
    
    # 입력된 수치(follower_count, calculated_speed)가 실시간으로 주입되는 Three.js 코드
    threejs_embed_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #1a1a1a; }}
            #canvas-container {{ width: 100vw; height: 100vh; position: relative; }}
            #info-overlay {{ 
                position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                color: white; font-family: sans-serif; font-size: 14px; font-weight: bold;
                background: rgba(0,0,0,0.8); padding: 12px 20px; border-radius: 20px; text-align: center;
                pointer-events: none; width: 85%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); line-height: 1.4;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
    <div id="canvas-container">
        <div id="info-overlay">⏳ 시뮬레이션 환경 구성 중...</div>
    </div>
    
    <script>
    const container = document.getElementById('canvas-container');
    const infoOverlay = document.getElementById('info-overlay');
    
    const CONTAINER_SIZE = 15;
    const VISUAL_USERS = 60; 
    const MAX_TARGET_USERS = {follower_count}; // 실시간 변경되는 팔로워 수 적용
    const BALL_RADIUS = 0.5;
    const sharing_speed = {calculated_speed};  // 실시간 변경되는 스토리 비례 속도 적용
    
    let time_elapsed = 0;
    let infected_visual_count = 1;
    let last_reported_time = 0;
    const dt = 0.02;
    
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, 600 / 500, 0.1, 1000);
    camera.position.set(0, 0, 35);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(600, 480);
    container.appendChild(renderer.domElement);
    
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);
    
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 2 }})
    );
    scene.add(boxWireframe);
    
    const users = [];
    const sphereGeom = new THREE.SphereGeometry(BALL_RADIUS, 16, 16);
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000, emissive: 0x330000, shininess: 50 }});
    
    const trailPoints = [];
    const maxTrailLength = 50; 
    const trailGeometry = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(maxTrailLength * 3);
    trailGeometry.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
    const trailMaterial = new THREE.LineBasicMaterial({{ color: 0xff3333, linewidth: 3, transparent: true, opacity: 0.7 }});
    const trailLine = new THREE.Line(trailGeometry, trailMaterial);
    scene.add(trailLine);
    
    for (let i = 0; i < VISUAL_USERS; i++) {{
        const isFirst = (i === 0);
        const mesh = new THREE.Mesh(sphereGeom, isFirst ? redMat : whiteMat);
        
        mesh.position.set(
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1),
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1),
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1)
        );
        scene.add(mesh);
        
        users.push({{
            mesh: mesh,
            velocity: new THREE.Vector3((Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1).normalize(),
            infected: isFirst
        }});
    }}
    
    let isDragging = false;
    let previousMousePosition = {{ x: 0, y: 0 }};
    window.addEventListener('mousedown', function(e) {{ isDragging = true; }});
    window.addEventListener('mousemove', function(e) {{
        const deltaMove = {{ x: e.offsetX - previousMousePosition.x, y: e.offsetY - previousMousePosition.y }};
        if (isDragging) {{
            boxWireframe.rotation.y += deltaMove.x * 0.005;
            boxWireframe.rotation.x += deltaMove.y * 0.005;
            users.forEach(u => {{
                u.mesh.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), deltaMove.x * 0.005);
                u.mesh.position.applyAxisAngle(new THREE.Vector3(1, 0, 0), deltaMove.y * 0.005);
                u.velocity.applyAxisAngle(new THREE.Vector3(0, 1, 0), deltaMove.x * 0.005);
                u.velocity.applyAxisAngle(new THREE.Vector3(1, 0, 0), deltaMove.y * 0.005);
            }});
        }}
        previousMousePosition = {{ x: e.offsetX, y: e.offsetY }};
    }});
    window.addEventListener('mouseup', function(e) {{ isDragging = false; }});
    
    function animate() {{
        requestAnimationFrame(animate);
        
        if (infected_visual_count < VISUAL_USERS) {{
            time_elapsed += dt;
        }}
        
        const infectionRatio = infected_visual_count / VISUAL_USERS;
        let scaledInfected = Math.floor(infectionRatio * MAX_TARGET_USERS);
        if (scaledInfected === 0 && infected_visual_count > 0) scaledInfected = 1;
        if (infected_visual_count === VISUAL_USERS) scaledInfected = MAX_TARGET_USERS;
        
        if (scaledInfected < MAX_TARGET_USERS) {{
            infoOverlay.innerHTML = "⏱️ 경과 시간: " + time_elapsed.toFixed(1) + "초<br>🚨 <span style='color:#ff4d4d;'>가상 피해 팔로워 수: " + scaledInfected.toLocaleString() + "명</span> / " + MAX_TARGET_USERS.toLocaleString() + "명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d; font-size:15px;'>전파 종료: 내 팔로워 " + MAX_TARGET_USERS.toLocaleString() + "명 전체 유출 완료</span><br>⏳ 총 확산 소요 시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        if (time_elapsed - last_reported_time > 0.2 && infected_visual_count <= VISUAL_USERS) {{
            window.parent.postMessage({{
                type: "streamlit_zombie_update",
                time: time_elapsed.toFixed(1),
                infected: scaledInfected
            }}, "*");
            last_reported_time = time_elapsed;
        }}
        
        for (let i = 0; i < users.length; i++) {{
            const u = users[i];
            u.mesh.position.x += u.velocity.x * sharing_speed * dt;
            u.mesh.position.y += u.velocity.y * sharing_speed * dt;
            u.mesh.position.z += u.velocity.z * sharing_speed * dt;
            
            const boundary = CONTAINER_SIZE - BALL_RADIUS;
            if (Math.abs(u.mesh.position.x) >= boundary) {{ u.velocity.x = -u.velocity.x; u.mesh.position.x = u.mesh.position.x > 0 ? boundary : -boundary; }}
            if (Math.abs(u.mesh.position.y) >= boundary) {{ u.velocity.y = -u.velocity.y; u.mesh.position.y = u.mesh.position.y > 0 ? boundary : -boundary; }}
            if (Math.abs(u.mesh.position.z) >= boundary) {{ u.velocity.z = -u.velocity.z; u.mesh.position.z = u.mesh.position.z > 0 ? boundary : -boundary; }}
        }}
        
        const firstUserPos = users[0].mesh.position;
        trailPoints.push(new THREE.Vector3(firstUserPos.x, firstUserPos.y, firstUserPos.z));
        if (trailPoints.length > maxTrailLength) {{ trailPoints.shift(); }}
        
        const positions = trailLine.geometry.attributes.position.array;
        for (let i = 0; i < maxTrailLength; i++) {{
            const pt = trailPoints[i] || firstUserPos;
            positions[i * 3] = pt.x; positions[i * 3 + 1] = pt.y; positions[i * 3 + 2] = pt.z;
        }}
        trailLine.geometry.attributes.position.needsUpdate = true;
        
        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                const u1 = users[i]; const u2 = users[j];
                const dist = u1.mesh.position.distanceTo(u2.mesh.position);
                if (dist < (BALL_RADIUS * 2)) {{
                    if (u1.infected && !u2.infected) {{ u2.mesh.material = redMat; u2.infected = true; infected_visual_count++; }}
                    else if (u2.infected && !u1.infected) {{ u1.mesh.material = redMat; u1.infected = true; infected_visual_count++; }}
                }}
            }}
        }}
        renderer.render(scene, camera);
    }}
    animate();
    </script>
    </body>
    </html>
    """
    
    components.html(threejs_embed_code, height=500, scrolling=False)

# 부모-자식 데이터 통신용 브릿지
st_components_listener = f"""
<script>
window.addEventListener("message", (event) => {{
    if (event.data && event.data.type === "streamlit_zombie_update") {{
        const data = event.data;
        const input = window.parent.document.getElementById("zombie_data_bridge");
        if (input) {{
            input.value = data.time + "," + data.infected;
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}
}});
</script>
"""
components.html(st_components_listener, height=0, width=0)

# 5. 실시간 동적 차트 출력 및 수업 가이드 영역
with col_chart:
    st.subheader("📈 설정 수치 기반 실시간 확산 속도 곡선")
    
    data_carrier = st.text_input("data_bridge", value="", key="zombie_data_bridge", label_visibility="collapsed")
    
    if data_carrier:
        try:
            t_val, inf_val = data_carrier.split(",")
            t_val = float(t_val)
            inf_val = int(inf_val)
            
            if t_val not in st.session_state.chart_data.index:
                new_row = pd.DataFrame([[inf_val]], columns=["피해 팔로워 수(명)"], index=[t_val])
                st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_row])
        except:
            pass

    if not st.session_state.chart_data.empty:
        st.line_chart(st.session_state.chart_data, height=260)
    else:
        st.info("왼쪽 슬라이더 수치를 조절하면 여기에 새로운 확산 곡선이 즉시 그려집니다.")

    # 🧑‍🏫 수치 변화에 따른 인과관계 가이드 카드
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: #f8fafc; color: #1e293b; border-left: 5px solid #64748b; margin-top: 10px;">
        ⚙️ <b>시뮬레이션 실시간 추적 데이터</b><br>
        • 설정된 총 팔로워(Y축 최대치): <b>{follower_count:,}명</b><br>
        • 내가 올린 스토리 수(가속도 인자): <b>{story_count}개</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📝 학생 탐구 과제 (수치 제어 및 실험)
    * **실험 1 (유출 빈도의 영향)**: 팔로워 수는 `500명`으로 고정하고, 스토리를 `1개` 올렸을 때와 `8개` 올렸을 때 그래프의 상승 각도가 어떻게 달라지는지 비교해 보세요. (스토리가 많을수록 노출 빈도가 늘어나 확산 속도가 수직 상승합니다.)
    * **실험 2 (네트워크 규모의 영향)**: 스토리는 `2개`로 고정하고, 팔로워 수를 `200명`에서 `10,000명`으로 올렸을 때 도달하는 인구의 폭발 규모를 그래프 눈금(Y축)을 통해 확인해 봅시다.
    """)

    if st.button("🔄 시뮬레이션 및 그래프 초기화"):
        st.session_state.chart_data = pd.DataFrame(columns=["시간(초)", "피해 유저 수(명)"]).set_index("시간(초)")
        st.rerun()
