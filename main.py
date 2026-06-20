import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 2차 네트워크 기반 정보 확산 실시간 시뮬레이션")
st.markdown("""
교과서 225쪽 **'디지털 공간의 정보 확산'** 단원 실습 앱입니다.  
왼쪽 제어창에서 환경을 바꾸어 보세요. 수치를 변경하는 즉시 **시간 경과에 따른 실시간 확산 그래프**가 하단에 동적으로 그려집니다.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

my_followers = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)", 
    min_value=10, 
    max_value=1000, 
    value=30, 
    step=10
)

friends_followers = st.sidebar.slider(
    "2. 내 친구들의 평균 팔로워 수 (명)", 
    min_value=10, 
    max_value=500, 
    value=100, 
    step=10
)

story_count = st.sidebar.slider(
    "3. 내가 올린 스토리/게시글 수 (개)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

# 💡 복합 네트워크 수식 연산 및 전파 속도 도출
total_potential_pool = int(my_followers * (1 + (friends_followers * 0.4)))
calculated_speed = story_count * (1 + (friends_followers * 0.01))

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **빨간 공**: 유출되어 정보가 확산된 유저
* ⚪ **하얀 공**: 아직 노출되지 않은 유저
* 🖱️ 3D 공간을 마우스 드래그하면 회전하여 볼 수 있습니다.
""")

# 교사용 가이드 숨김 메뉴
st.sidebar.markdown("---")
with st.sidebar.expander("🔐 💡 교사용 수업 가이드 (선생님만 클릭!)"):
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0fdf4; color: #166534; border-left: 4px solid #22c55e; font-size: 13px;">
        <b>현재 시뮬레이션 연산 데이터</b><br>
        • 내 직접 팔로워: <b>{my_followers}명</b><br>
        • 건너건너 연결된 잠재 피해 규모: <b>{total_potential_pool:,}명</b>
    </div>
    """, unsafe_allow_html=True)
    st.caption("""
    📢 **선생님 한마디 & 지도 팁**
    "얘들아, 내 팔로워는 30명뿐이지만 우측 하단 그래프가 실시간으로 치솟는 걸 보렴. 
    시간이 지나면서 친구의 친구들이 확인하는 순간 기울기가 무섭게 급해지지? 
    이게 바로 인터넷 공간에서 단 한 번의 유출이 걷잡을 수 없는 대재앙이 되는 이유란다."
    """)

# 3. 메인 화면 구성 (3D와 그래프를 한 프레임 안에 묶어 실시간 유기적 동기화 구현)
col_main, col_empty = st.columns([1.8, 0.2])

with col_main:
    # 3D 물리 엔진의 프레임과 Chart.js를 완벽하게 동기화시킨 임베드 시스템
    combined_embedded_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background-color: #1a1a1a; font-family: sans-serif; color: white; overflow: hidden; }}
            #canvas-container {{ width: 100%; height: 340px; position: relative; background: #1a1a1a; }}
            #info-overlay {{ 
                position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                color: white; font-size: 13px; font-weight: bold;
                background: rgba(0,0,0,0.8); padding: 8px 16px; border-radius: 20px; text-align: center;
                pointer-events: none; width: 85%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10;
            }}
            #chart-container {{ width: 98%; margin: 10px auto; background: #262626; padding: 15px; border-radius: 10px; box-sizing: border-box; position: relative; }}
            h4 {{ margin: 0 0 8px 0; color: #cbd5e1; font-size: 14px; }}
            .reset-btn {{
                position: absolute; right: 15px; top: 10px;
                background-color: #ef4444; color: white; border: none;
                padding: 5px 10px; font-size: 11px; font-weight: bold;
                border-radius: 4px; cursor: pointer;
            }}
            .reset-btn:hover {{ background-color: #dc2626; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>

    <div id="canvas-container">
        <div id="info-overlay">⏳ 시뮬레이터를 로드 중입니다...</div>
    </div>

    <div id="chart-container">
        <h4>📊 시간 경과에 따른 누적 확산 유저 수 (실시간 드로잉)</h4>
        <button class="reset-btn" onclick="resetAll()">🔄 시뮬레이션 처음부터 다시 시작</button>
        <canvas id="realtimeChart" height="90"></canvas>
    </div>
    
    <script>
    const container = document.getElementById('canvas-container');
    const infoOverlay = document.getElementById('info-overlay');
    
    const CONTAINER_SIZE = 13;
    const VISUAL_USERS = 60;
    const MAX_TARGET_USERS = {total_potential_pool}; 
    const sharing_speed = {calculated_speed};
    const dt = 0.02;
    
    let time_elapsed = 0;
    let infected_visual_count = 1;
    let last_chart_update_time = 0;
    
    // --- 📊 실시간 Chart.js 초기화 및 인스턴스 핸들링 ---
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    let realtimeChart;
    
    function initChart() {{
        if(realtimeChart) {{ realtimeChart.destroy(); }}
        realtimeChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: [0],
                datasets: [{{
                    label: '피해 인원 (명)',
                    data: [1],
                    borderColor: '#ff4d4d',
                    backgroundColor: 'rgba(255, 77, 77, 0.08)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                animation: false, // 실시간 드로잉을 위해 불필요한 차트 내부 애니메이션 비활성화
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ title: {{ display: true, text: '경과 시간 (초)', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#404040' }} }},
                    y: {{ title: {{ display: true, text: '총 피해 (명)', color: '#94a3b8' }}, min: 0, max: MAX_TARGET_USERS, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#404040' }} }}
                }}
            }}
        }});
    }}
    
    // --- 🎮 Three.js 물리 엔진 무대 구축 ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 340, 0.1, 1000);
    camera.position.set(0, 0, 30);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(container.clientWidth, 340);
    container.appendChild(renderer.domElement);
    
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.4);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);
    
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0x555555, linewidth: 1.2 }})
    );
    scene.add(boxWireframe);
    
    let users = [];
    const sphereGeom = new THREE.SphereGeometry(0.5, 16, 16);
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000, emissive: 0x220000, shininess: 50 }});
    
    function setupUsers() {{
        users.forEach(u => {{ scene.remove(u.mesh); }});
        users = [];
        for (let i = 0; i < VISUAL_USERS; i++) {{
            const isFirst = (i === 0);
            const mesh = new THREE.Mesh(sphereGeom, isFirst ? redMat : whiteMat);
            mesh.position.set((Math.random()*24)-12, (Math.random()*24)-12, (Math.random()*24)-12);
            scene.add(mesh);
            users.push({{ mesh: mesh, velocity: new THREE.Vector3((Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1).normalize(), infected: isFirst }});
        }}
    }}
    
    // 🖱️ 마우스 회전 인터랙션 구현
    let isDragging = false;
    let previousMousePosition = {{ x: 0, y: 0 }};
    window.addEventListener('mousedown', () => {{ isDragging = true; }});
    window.addEventListener('mousemove', (e) => {{
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
    window.addEventListener('mouseup', () => {{ isDragging = false; }});
    
    // 🔄 완전 리셋 트리거 함수
    window.resetAll = function() {{
        time_elapsed = 0;
        infected_visual_count = 1;
        last_chart_update_time = 0;
        initChart();
        setupUsers();
    }}
    
    // --- 🎮 실시간 연동 메인 그래픽스 루프 ---
    function animate() {{
        requestAnimationFrame(animate);
        
        if (infected_visual_count < VISUAL_USERS) {{
            time_elapsed += dt;
        }}
        
        // 3D 물리 감염률을 실제 스케일링 인구수에 투영 연산
        const infectionRatio = infected_visual_count / VISUAL_USERS;
        let scaledInfected = Math.floor(infectionRatio * MAX_TARGET_USERS);
        if (scaledInfected === 0 && infected_visual_count > 0) scaledInfected = 1;
        if (infected_visual_count === VISUAL_USERS) scaledInfected = MAX_TARGET_USERS;
        
        // 상단 텍스트 전광판 실시간 정보 갱신
        if (scaledInfected < MAX_TARGET_USERS) {{
            infoOverlay.innerHTML = "⏱️ 경과 시간: " + time_elapsed.toFixed(1) + "초 | 🚨 <span style='color:#ff4d4d;'>누적 확산 피해: " + scaledInfected.toLocaleString() + "명</span> / " + MAX_TARGET_USERS.toLocaleString() + "명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d;'>전파 완료: 네트워크 내 " + MAX_TARGET_USERS.toLocaleString() + "명 전원 유출</span> | ⏳ 총 소요시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        // 💡 핵심: 0.15초마다 자바스크립트 차트에 데이터를 실시간으로 Push하여 실시간 시각화!
        if (time_elapsed - last_chart_update_time > 0.15 && infected_visual_count <= VISUAL_USERS) {{
            realtimeChart.data.labels.push(time_elapsed.toFixed(1));
            realtimeChart.data.datasets[0].data.push(scaledInfected);
            realtimeChart.update(); // 선 그래프 동적 렌더링
            last_chart_update_time = time_elapsed;
        }}
        
        // 3D 공들의 프레임 이동 및 경계선 충돌 물리 연산
        for (let i = 0; i < users.length; i++) {{
            const u = users[i];
            u.mesh.position.addScaledVector(u.velocity, sharing_speed * dt);
            
            const b = CONTAINER_SIZE - 0.5;
            if (Math.abs(u.mesh.position.x) >= b) {{ u.velocity.x *= -1; u.mesh.position.x = u.mesh.position.x > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.y) >= b) {{ u.velocity.y *= -1; u.mesh.position.y = u.mesh.position.y > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.z) >= b) {{ u.velocity.z *= -1; u.mesh.position.z = u.mesh.position.z > 0 ? b : -b; }}
        }}
        
        // 공들끼리 마주쳤을 때 감염 전파 매커니즘
        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                if (users[i].mesh.position.distanceTo(users[j].mesh.position) < 1.0) {{
                    if (users[i].infected && !users[j].infected) {{ users[j].mesh.material = redMat; users[j].infected = true; infected_visual_count++; }}
                    else if (users[j].infected && !users[i].infected) {{ users[i].mesh.material = redMat; users[i].infected = true; infected_visual_count++; }}
                }}
            }}
        }}
        
        boxWireframe.rotation.y += 0.001; // 공간 미세 자동 회전
        renderer.render(scene, camera);
    }}
    
    // 빌드 기동
    initChart();
    setupUsers();
    animate();
    </script>
    </body>
    </html>
    """
    components.html(combined_embedded_code, height=540, scrolling=False)
