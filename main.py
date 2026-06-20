import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 내 SNS 설정에 따른 개인정보 확산 속도 시뮬레이션")
st.markdown("""
교과서 225쪽 **'디지털 공간의 정보 확산'** 단원 실습 앱입니다.  
왼쪽 제어창에서 **'나의 팔로워 수'**와 **'내가 올린 스토리 수'**를 자유롭게 바꾸어 보세요.   
수치를 변경하는 즉시 3D 유출 궤적과 **하단의 실시간 확산 속도 그래프**가 유기적으로 연동되어 완전히 달라집니다.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

follower_count = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)", 
    min_value=10, 
    max_value=2000, 
    value=50, 
    step=10
)

story_count = st.sidebar.slider(
    "2. 내가 올린 스토리/게시글 수 (개)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

calculated_speed = story_count * 2.5

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **궤적이 남는 빨간 공**: 유출된 스토리/게시글 (최초 유출자)
* ⚪ **하얀 공**: 내 스토리를 본 팔로워 및 일반 유저들
* 🖱️ 3D 화면을 마우스 드래그하면 공간을 돌려볼 수 있습니다.
""")

# 교사용 가이드 숨김 메뉴
st.sidebar.markdown("---")
with st.sidebar.expander("🔐 💡 교사용 수업 가이드 (선생님만 클릭!)"):
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0fdf4; color: #166534; border-left: 4px solid #22c55e; font-size: 13px;">
        <b>현재 세팅 요약</b><br>
        • 학생 설정 팔로워: <b>{follower_count}명</b><br>
        • 학생 설정 스토리: <b>{story_count}개</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("""
    📢 **선생님 한마디 & 지도 팁**
    "얘들아, 내 팔로워가 10명밖에 안 된다고 해서 내가 올린 비밀이나 사진이 안전할까? 
    내가 올린 스토리 수가 많아지면 하단 그래프의 기울기가 엄청나게 가팔라지는 걸 봐봐. 
    결국 디지털 세상에서는 내가 단 10명에게만 보여준 이야기라도 순식간에 외부로 퍼져나갈 수 있어!"
    """)

# 3. 메인 레이아웃 출력
col_sim, col_empty = st.columns([1.8, 0.2])

with col_sim:
    combined_embed_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background-color: #1a1a1a; font-family: sans-serif; color: white; overflow-x: hidden; }}
            #canvas-container {{ width: 100%; height: 380px; position: relative; background: #1a1a1a; }}
            #info-overlay {{ 
                position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                color: white; font-size: 13px; font-weight: bold;
                background: rgba(0,0,0,0.8); padding: 8px 16px; border-radius: 20px; text-align: center;
                pointer-events: none; width: 80%; box-shadow: 0 4px 10px rgba(0,0,0,0.5); line-height: 1.4; z-index: 10;
            }}
            #chart-container {{ width: 95%; margin: 15px auto; background: #262626; padding: 15px; border-radius: 10px; box-sizing: border-box; position: relative; }}
            h4 {{ margin: 0 0 10px 0; color: #cbd5e1; font-size: 14px; }}
            .reset-btn {{
                position: absolute; right: 15px; top: 10px;
                background-color: #ef4444; color: white; border: none;
                padding: 6px 12px; font-size: 12px; font-weight: bold;
                border-radius: 5px; cursor: pointer; transition: background 0.2s;
            }}
            .reset-btn:hover {{ background-color: #dc2626; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>

    <div id="canvas-container">
        <div id="info-overlay">⏳ 시뮬레이션 공간 구성 중...</div>
    </div>

    <div id="chart-container">
        <h4>선택 수치 기반 실시간 확산 속도 곡선 (Y축 최대치: {follower_count:,}명 규모)</h4>
        <button class="reset-btn" onclick="resetSimulation()">🔄 시뮬레이션 리셋</button>
        <canvas id="realtimeChart" height="100"></canvas>
    </div>
    
    <script>
    const container = document.getElementById('canvas-container');
    const infoOverlay = document.getElementById('info-overlay');
    
    const CONTAINER_SIZE = 14;
    const VISUAL_USERS = 60; 
    const MAX_TARGET_USERS = {follower_count}; 
    const BALL_RADIUS = 0.5;
    const sharing_speed = {calculated_speed};  
    
    let time_elapsed = 0;
    let infected_visual_count = 1;
    let last_chart_update_time = 0;
    const dt = 0.02;
    
    // --- Chart.js 초기화 ---
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    let realtimeChart;
    
    function initChart() {{
        if(realtimeChart) {{ realtimeChart.destroy(); }}
        realtimeChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: [0],
                datasets: [{{
                    label: '피해 팔로워 수 (명)',
                    data: [1],
                    borderColor: '#ff4d4d',
                    backgroundColor: 'rgba(255, 77, 77, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ title: {{ display: true, text: '시간 (초)', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#404040' }} }},
                    y: {{ title: {{ display: true, text: '피해 인원 (명)', color: '#94a3b8' }}, min: 0, max: MAX_TARGET_USERS, ticks: {{ color: '#94a3b8' }}, grid: '#404040' }}
                }}
            }}
        }});
    }}
    
    // --- Three.js 초기화 ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 380, 0.1, 1000);
    camera.position.set(0, 0, 32);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(container.clientWidth, 380);
    container.appendChild(renderer.domElement);
    
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.4);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);
    
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 1.5 }})
    );
    scene.add(boxWireframe);
    
    let users = [];
    const sphereGeom = new THREE.SphereGeometry(BALL_RADIUS, 16, 16);
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000, emissive: 0x220000, shininess: 50 }});
    
    const trailPoints = [];
    const maxTrailLength = 40; 
    const trailGeometry = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(maxTrailLength * 3);
    trailGeometry.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
    const trailMaterial = new THREE.LineBasicMaterial({{ color: 0xff4d4d, linewidth: 2.5, transparent: true, opacity: 0.8 }});
    const trailLine = new THREE.Line(trailGeometry, trailMaterial);
    scene.add(trailLine);
    
    // 💡 무대 청소 로직을 추가하여 중복 생성 방지
    function setupUsers() {{
        // 기존에 생성되어 scene에 존재하던 유저 메쉬들을 완벽하게 제거
        users.forEach(u => {{
            scene.remove(u.mesh);
            if(u.mesh.geometry) u.mesh.geometry.dispose();
            if(u.mesh.material) u.mesh.material.dispose();
        }});
        
        users = []; // 배열 초기화
        
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
    }}
    
    // 드래그 제어
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
    
    // 완벽한 리셋 함수
    window.resetSimulation = function() {{
        time_elapsed = 0;
        infected_visual_count = 1;
        last_chart_update_time = 0;
        trailPoints.length = 0;
        initChart();
        setupUsers();
    }}
    
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
            infoOverlay.innerHTML = "⏱️ 경과 시간: " + time_elapsed.toFixed(1) + "초 | 🚨 <span style='color:#ff4d4d;'>피해 팔로워 수: " + scaledInfected.toLocaleString() + "명</span> / " + MAX_TARGET_USERS.toLocaleString() + "명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d; font-size:14px;'>전파 종료: 내 팔로워 " + MAX_TARGET_USERS.toLocaleString() + "명 전체 유출 완료</span> | ⏳ 소요 시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        if (time_elapsed - last_chart_update_time > 0.15 && infected_visual_count <= VISUAL_USERS) {{
            realtimeChart.data.labels.push(time_elapsed.toFixed(1));
            realtimeChart.data.datasets[0].data.push(scaledInfected);
            realtimeChart.update('none'); 
            last_chart_update_time = time_elapsed;
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
        
        const firstUserPos = users[0]?.mesh?.position || new THREE.Vector3();
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
    
    initChart();
    setupUsers();
    animate();
    </script>
    </body>
    </html>
    """
    
    components.html(combined_embed_code, height=620, scrolling=False)
