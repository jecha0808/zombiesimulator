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

# 2. 사이드바 인터페이스 구성 (아이들 눈높이에 맞춘 세밀한 수치 조정)
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

# 💡 최소 수치를 10명으로 전격 대폭 낮추고, 10명 단위로 조절 가능하게 수정!
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

# 스토리 수에 비례한 확산 속도 가중치 계산
calculated_speed = story_count * 2.5

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **궤적이 남는 빨간 공**: 유출된 스토리/게시글 (최초 유출자)
* ⚪ **하얀 공**: 내 스토리를 본 팔로워 및 일반 유저들
* 🖱️ 3D 화면을 마우스 드래그하면 공간을 돌려볼 수 있습니다.
""")

# 3. 레이아웃 분할 (좌측: 3D 시뮬레이터 및 실시간 차트 통합 브라우저 / 우측: 탐구 활동 발문)
col_sim, col_guide = st.columns([1.3, 0.7])

with col_sim:
    st.subheader("🎮 3D 확산 가상 공간 & 실시간 통계 그래프")
    
    # 3D 렌더러와 고성능 Chart.js 그래프를 한 컨텍스트 안에 묶어 동기화 오류를 원천 차단한 HTML/JS 템플릿
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
            #chart-container {{ width: 95%; margin: 15px auto; background: #262626; padding: 15px; border-radius: 10px; box-sizing: border-box; }}
            h4 {{ margin: 0 0 10px 0; color: #cbd5e1; font-size: 14px; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>

    <div id="canvas-container">
        <div id="info-overlay">⏳ 시뮬레이션 공간 구성 중...</div>
    </div>

    <div id="chart-container">
        <h4>📈 실시간 정보 확산 속도 곡선 (Y축 최대치: {follower_count:,}명 규모)</h4>
        <canvas id="realtimeChart" height="110"></canvas>
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
    
    // --- Chart.js 초기화 로직 ---
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    const chartData = {{
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
    }};
    const config = {{
        type: 'line',
        data: chartData,
        options: {{
            responsive: true,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                x: {{ title: {{ display: true, text: '시간 (초)', color: '#94a3b8' }}, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#404040' }} }},
                y: {{ title: {{ display: true, text: '피해 인원 (명)', color: '#94a3b8' }}, min: 0, max: MAX_TARGET_USERS, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#404040' }} }}
            }}
        }}
    }};
    const realtimeChart = new Chart(ctx, config);
    
    // --- Three.js 3D 환경 빌드 ---
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
    
    const users = [];
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
    
    components.html(combined_embed_code, height=600, scrolling=False)

with col_guide:
    st.subheader("🧑‍🏫 중학교 정보윤리 실습 가이드")
    
    st.markdown(f"""
    <div style="padding: 12px; border-radius: 8px; background-color: #f8fafc; color: #1e293b; border-left: 5px solid #10b981; margin-bottom: 15px;">
        ⚙️ <b>내 SNS 실시간 반영 데이터</b><br>
        • 나의 실제 팔로워 규모: <b>{follower_count}명</b><br>
        • 내가 올린 스토리 수: <b>{story_count}개</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    📢 **소규모 네트워크(팔로워 10~50명) 수업 지도 팁**
    
    "얘들아, 내 팔로워가 10명밖에 안 된다고 해서 내가 올린 비밀이나 사진이 안전할까? 
    내가 올린 스토리 수가 많아지면 하단 그래프의 기울기가 엄청나게 가팔라지는 걸 봐봐. 
    
    비록 내 팔로워는 10명이지만, 그 10명의 친구들에게도 각자 10명씩의 또 다른 팔로워들이 겹겹이 연결되어 있단다. 결국 디지털 세상에서는 내가 단 10명에게만 보여준 이야기라도 궤적(선)을 그리며 순식간에 외부로 퍼져나갈 수 있어!"
    """)
    
    if st.button("🔄 시뮬레이션 및 그래프 처음부터 다시 시작"):
        st.rerun()
