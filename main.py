import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="[디지털 윤리] 정보 확산 속도 체험하기",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 [디지털 윤리] 정보 확산 속도 체험하기")
st.markdown("""
교과서 225쪽 실습 앱입니다. 인터넷 공간 상에서 정보가 얼마나 빠르게 확산 하는지 직접 체험해 봅시다!
""")

st.sidebar.header("⚙️ 시뮬레이션 환경 설정")

my_followers = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)",
    min_value=0, max_value=1000, value=30, step=10
)
friends_followers = st.sidebar.slider(
    "2. 내 친구들의 평균 팔로워 수 (명)",
    min_value=0, max_value=500, value=100, step=10
)
story_count = st.sidebar.slider(
    "3. 게시글 확산 빈도 (단위)",
    min_value=1, max_value=10, value=2, step=1
)

# 누적 피해 풀 & 속도 (최소 1 보장)
total_potential_pool = max(1, int(my_followers * (1 + (friends_followers * 0.4))))
calculated_speed = story_count * (1 + (friends_followers * 0.01))

# ───── 시각화 공 개수 계산 ─────
def map_followers(val, threshold, slider_max, max_extra):
    if val <= threshold:
        return val
    else:
        ratio = (val - threshold) / (slider_max - threshold)
        return threshold + int(ratio * max_extra)

if my_followers == 0:
    visual_my = 0
    visual_extended = 0
else:
    visual_my       = map_followers(my_followers,      threshold=100, slider_max=1000, max_extra=50)
    visual_extended = map_followers(friends_followers, threshold=500, slider_max=500,  max_extra=0)

VISUAL_USERS = max(1, min(400, visual_my + visual_extended))

# 사이드바 안내
st.sidebar.markdown("---")
st.sidebar.metric(
    label="🎯 현재 시뮬레이션 공 개수",
    value=f"{VISUAL_USERS}개",
    help=(
    "내 팔로워가 0이면 정보가 퍼지지 않으므로 본인 1명만 표시됩니다.\n\n"
    "**계산식:**\n\n"
    "내 팔로워 + (내 팔로워 × 친구 팔로워 × 40%)\n\n"
    "= 피해 규모"
    )
)

if my_followers == 0:
    st.sidebar.caption(
        f"⛔ **내 팔로워가 0명이라 정보가 어디로도 퍼지지 않습니다.**\n\n"
        f"• 시뮬레이션 인원: **본인 1명**\n\n"
        f"• 누적 피해 규모(수치): **0명**"
    )
else:
    exact_my       = "✅ 1:1" if my_followers <= 100 else "📦 압축"
    exact_extended = "✅ 1:1"
    st.sidebar.caption(
        f"• 내 직접 영향권: **{visual_my}명** ({exact_my})\n\n"
        f"• 친구의 친구까지: **+{visual_extended}명** ({exact_extended})\n\n"
        f"• 누적 피해 규모(수치): **{total_potential_pool:,}명**"
    )

if VISUAL_USERS >= 350:
    st.sidebar.warning("⚠️ 공이 매우 많아 브라우저 성능에 따라 다소 버벅일 수 있습니다.")

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 조작 가이드**
* 🖱️ **마우스 오른쪽 버튼**을 누른 상태로 3D 공간을 **드래그**하면 회전합니다.
* 휠을 스크롤하면 **확대/축소(Zoom)**가 가능합니다.
""")

# 메인 임베디드 HTML
combined_embedded_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ 
            margin: 0; padding: 0; background-color: #1a1a1a; 
            font-family: sans-serif; color: white; overflow: hidden;
            display: flex; flex-direction: column; height: 100vh;
        }}
        #canvas-container {{ 
            width: 100%; height: 53vh; position: relative; background: #141414; 
            border-bottom: 2px solid #333;
        }}
        #info-overlay {{ 
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            color: #00f2ff; font-size: 15px; font-weight: bold;
            background: rgba(0,0,0,0.85); padding: 8px 22px; border-radius: 30px;
            z-index: 10; border: 1px solid #333; text-align: center;
        }}
        #ball-count-badge {{
            position: absolute; top: 15px; left: 15px;
            color: #ffd166; font-size: 12px; font-weight: bold;
            background: rgba(0,0,0,0.85); padding: 6px 14px; border-radius: 6px;
            z-index: 10; border: 1px solid #333;
        }}
        #chart-container {{ 
            width: 96%; margin: auto; height: 37vh;
            background: #222222; padding: 15px; border-radius: 12px;
            box-sizing: border-box; position: relative;
        }}
        h4 {{ margin: 0 0 10px 0; color: #cbd5e1; font-size: 14px; text-align: center; }}
        .reset-btn {{
            position: absolute; right: 20px; top: 10px;
            background-color: #ef4444; color: white; border: none;
            padding: 5px 10px; font-size: 11px; font-weight: bold;
            border-radius: 4px; cursor: pointer; z-index: 20;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

<div id="canvas-container">
    <div id="ball-count-badge">🟢 사용자 수: {VISUAL_USERS}명</div>
    <div id="info-overlay">⏳ 시뮬레이션 준비 중...</div>
</div>

<div id="chart-container">
    <h4>📊 확산 추이 분석 (누적 피해 규모: {total_potential_pool:,}명 기준)</h4>
    <button class="reset-btn" onclick="resetAll()">🔄 시뮬레이션 리셋</button>
    <canvas id="realtimeChart"></canvas>
</div>

<script>
    const container = document.getElementById('canvas-container');
    const infoOverlay = document.getElementById('info-overlay');

    const VISUAL_USERS = {VISUAL_USERS};
    const MAX_TARGET_USERS = {total_potential_pool};
    const sharing_speed = {calculated_speed};
    const dt = 0.02;

    const sphereRadius = VISUAL_USERS > 300 ? 0.20
                       : VISUAL_USERS > 150 ? 0.28
                       : VISUAL_USERS > 80  ? 0.36
                       : 0.48;
    const collisionDist = sphereRadius * 2.2;

    let time_elapsed = 0;
    let infected_visual_count = 1;
    let last_chart_update_time = 0;

    const ctx = document.getElementById('realtimeChart').getContext('2d');
    let realtimeChart = new Chart(ctx, {{
        type: 'line',
        data: {{ labels: [0], datasets: [{{
            label: '피해 인원', data: [1], borderColor: '#ff4d4d',
            backgroundColor: 'rgba(255, 77, 77, 0.1)', borderWidth: 2.5, fill: true, tension: 0.3, pointRadius: 0
        }}] }},
        options: {{
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: {{
                x: {{ grid: {{ color: '#333' }}, ticks: {{ color: '#94a3b8' }} }},
                y: {{ min: 0, max: MAX_TARGET_USERS, grid: {{ color: '#333' }}, ticks: {{ color: '#94a3b8' }} }}
            }},
            plugins: {{ legend: {{ display: false }} }}
        }}
    }});

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 45);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    window.addEventListener('wheel', (e) => {{
        camera.position.z += e.deltaY * 0.02;
        camera.position.z = Math.max(20, Math.min(camera.position.z, 80));
    }}, {{ passive: true }});

    window.addEventListener('resize', () => {{
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }});

    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.4);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);

    const BOX_SIZE = 12;
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(BOX_SIZE * 2, BOX_SIZE * 2, BOX_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0x555555, linewidth: 1.0 }})
    );
    scene.add(boxWireframe);

    let users = [];
    const sphereGeom = new THREE.SphereGeometry(sphereRadius, 16, 16);
    const redMat   = new THREE.MeshPhongMaterial({{ color: 0xff4d4d, emissive: 0x220000, shininess: 50 }});
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});

    function setupUsers() {{
        users.forEach(u => scene.remove(u.mesh));
        users = [];
        for (let i = 0; i < VISUAL_USERS; i++) {{
            const isFirst = (i === 0);
            const mesh = new THREE.Mesh(sphereGeom, isFirst ? redMat : whiteMat);
            mesh.position.set((Math.random()*22)-11, (Math.random()*22)-11, (Math.random()*22)-11);
            scene.add(mesh);
            users.push({{
                mesh: mesh,
                velocity: new THREE.Vector3((Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1).normalize(),
                infected: isFirst
            }});
        }}
    }}

    let isDragging = false;
    let previousMousePosition = {{ x: 0, y: 0 }};
    container.addEventListener('mousedown', () => {{ isDragging = true; }});
    container.addEventListener('mousemove', (e) => {{
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

    window.resetAll = () => {{
        time_elapsed = 0; infected_visual_count = 1; last_chart_update_time = 0;
        realtimeChart.data.labels = [0]; realtimeChart.data.datasets[0].data = [1];
        realtimeChart.update(); setupUsers();
    }};

    function animate() {{
        requestAnimationFrame(animate);
        if (infected_visual_count < VISUAL_USERS) time_elapsed += dt;

        let scaled = Math.min(MAX_TARGET_USERS, Math.floor((infected_visual_count/VISUAL_USERS) * MAX_TARGET_USERS));
        if (scaled === 0 && infected_visual_count > 0) scaled = 1;
        if (infected_visual_count === VISUAL_USERS) scaled = MAX_TARGET_USERS;

        if (scaled < MAX_TARGET_USERS) {{
            infoOverlay.innerHTML = "⏱️ 경과: " + time_elapsed.toFixed(1) + "초 | 🚨 <span style='color:#ff4d4d;'>누적 확산 피해: " + scaled.toLocaleString() + "명</span> / " + MAX_TARGET_USERS.toLocaleString() + "명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d;'>전파 완료: 네트워크 내 " + MAX_TARGET_USERS.toLocaleString() + "명 전체 유출</span>";
        }}

        if (time_elapsed - last_chart_update_time > 0.15 && infected_visual_count <= VISUAL_USERS) {{
            realtimeChart.data.labels.push(time_elapsed.toFixed(1));
            realtimeChart.data.datasets[0].data.push(scaled);
            realtimeChart.update();
            last_chart_update_time = time_elapsed;
        }}

        const b = BOX_SIZE - 0.5;
        users.forEach(u => {{
            u.mesh.position.addScaledVector(u.velocity, sharing_speed * dt);
            if (Math.abs(u.mesh.position.x) >= b) {{ u.velocity.x *= -1; u.mesh.position.x = u.mesh.position.x > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.y) >= b) {{ u.velocity.y *= -1; u.mesh.position.y = u.mesh.position.y > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.z) >= b) {{ u.velocity.z *= -1; u.mesh.position.z = u.mesh.position.z > 0 ? b : -b; }}
        }});

        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                if (users[i].mesh.position.distanceTo(users[j].mesh.position) < collisionDist) {{
                    if (users[i].infected && !users[j].infected) {{ users[j].mesh.material = redMat; users[j].infected = true; infected_visual_count++; }}
                    else if (users[j].infected && !users[i].infected) {{ users[i].mesh.material = redMat; users[i].infected = true; infected_visual_count++; }}
                }}
            }}
        }}

        boxWireframe.rotation.y += 0.001;
        renderer.render(scene, camera);
    }}

    setupUsers();
    animate();
</script>
</body>
</html>
"""


components.html(combined_embedded_code, height=850, scrolling=False)
