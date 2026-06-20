import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터 (확장판)", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 2차 네트워크 기반 정보 확산 시뮬레이션")
st.markdown("""
교과서 225쪽 실습 앱의 **확장 버전**입니다. 시뮬레이터와 그래프 공간을 극대화하여 확산 과정을 더 정밀하게 관찰할 수 있습니다.
""")

# 2. 사이드바 인터페이스 구성
st.sidebar.header("⚙️ 시뮬레이션 환경 설정")

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
    "3. 게시글 확산 빈도 (단위)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

total_potential_pool = int(my_followers * (1 + (friends_followers * 0.4)))
calculated_speed = story_count * (1 + (friends_followers * 0.01))

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 조작 가이드**
* 🖱️ 3D 공간을 **드래그**하면 회전합니다.
* 휠을 사용해 **확대/축소**가 가능합니다.
""")

# 3. 메인 화면 구성
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
        /* 🚀 3D 시뮬레이터 공간을 화면 높이의 55%로 확장 */
        #canvas-container {{ 
            width: 100%; height: 55vh; position: relative; background: #000; 
            border-bottom: 2px solid #333;
        }}
        #info-overlay {{ 
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            color: #00f2ff; font-size: 16px; font-weight: bold;
            background: rgba(0,0,0,0.8); padding: 10px 25px; border-radius: 30px;
            z-index: 10; border: 1px solid #00f2ff;
        }}
        /* 🚀 그래프 공간을 화면 높이의 35%로 확장 */
        #chart-container {{ 
            width: 96%; margin: auto; height: 35vh;
            background: #262626; padding: 15px; border-radius: 12px;
            box-sizing: border-box; position: relative;
        }}
        h4 {{ margin: 0 0 10px 0; color: #cbd5e1; font-size: 14px; text-align: center; }}
        .reset-btn {{
            position: absolute; right: 20px; top: 10px;
            background-color: #ef4444; color: white; border: none;
            padding: 6px 12px; font-size: 12px; font-weight: bold;
            border-radius: 6px; cursor: pointer; z-index: 20;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

<div id="canvas-container">
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
    
    const VISUAL_USERS = 80; // 시각적 밀도 상향
    const MAX_TARGET_USERS = {total_potential_pool}; 
    const sharing_speed = {calculated_speed};
    const dt = 0.02;
    
    let time_elapsed = 0;
    let infected_visual_count = 1;
    let last_chart_update_time = 0;
    
    // --- 📊 Chart.js 설정 (반응형 높이 활성화) ---
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    let realtimeChart = new Chart(ctx, {{
        type: 'line',
        data: {{ labels: [0], datasets: [{{
            label: '피해 인원', data: [1], borderColor: '#00f2ff',
            backgroundColor: 'rgba(0, 242, 255, 0.1)', borderWidth: 3, fill: true, tension: 0.4, pointRadius: 0
        }}] }},
        options: {{
            responsive: true,
            maintainAspectRatio: false, // 🚀 컨테이너 크기에 맞게 세로 확장
            animation: false,
            scales: {{
                x: {{ grid: {{ color: '#444' }}, ticks: {{ color: '#94a3b8' }} }},
                y: {{ min: 0, max: MAX_TARGET_USERS, grid: {{ color: '#444' }}, ticks: {{ color: '#94a3b8' }} }}
            }},
            plugins: {{ legend: {{ display: false }} }}
        }}
    }});

    // --- 🎮 Three.js 무대 구축 ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 30;
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // 창 크기 변경 시 자동 리사이징
    window.addEventListener('resize', () => {{
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    }});

    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    
    let users = [];
    const sphereGeom = new THREE.SphereGeometry(0.6, 24, 24);
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff4d4d, emissive: 0x330000 }});
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, transparent: true, opacity: 0.7 }});

    function setupUsers() {{
        users.forEach(u => scene.remove(u.mesh));
        users = [];
        for (let i = 0; i < VISUAL_USERS; i++) {{
            const mesh = new THREE.Mesh(sphereGeom, i === 0 ? redMat : whiteMat);
            mesh.position.set((Math.random()-0.5)*40, (Math.random()-0.5)*40, (Math.random()-0.5)*40);
            scene.add(mesh);
            users.push({{ 
                mesh, infected: i === 0, 
                vel: new THREE.Vector3(Math.random()-0.5, Math.random()-0.5, Math.random()-0.5).multiplyScalar(0.5) 
            }});
        }}
    }}

    window.resetAll = () => {{
        time_elapsed = 0; infected_visual_count = 1; last_chart_update_time = 0;
        realtimeChart.data.labels = [0]; realtimeChart.data.datasets[0].data = [1];
        realtimeChart.update(); setupUsers();
    }};

    function animate() {{
        requestAnimationFrame(animate);
        if (infected_visual_count < VISUAL_USERS) time_elapsed += dt;

        let scaled = Math.min(MAX_TARGET_USERS, Math.floor((infected_visual_count/VISUAL_USERS) * MAX_TARGET_USERS));
        infoOverlay.innerHTML = `⏱️ ${{time_elapsed.toFixed(1)}}s | 🚨 피해 확산: ${{scaled.toLocaleString()}}명`;

        if (time_elapsed - last_chart_update_time > 0.2) {{
            realtimeChart.data.labels.push(time_elapsed.toFixed(1));
            realtimeChart.data.datasets[0].data.push(scaled);
            realtimeChart.update();
            last_chart_update_time = time_elapsed;
        }}

        users.forEach(u => {{
            u.mesh.position.addScaledVector(u.vel, sharing_speed);
            ['x','y','z'].forEach(axis => {{
                if (Math.abs(u.mesh.position[axis]) > 20) u.vel[axis] *= -1;
            }});
        }});

        // 충돌 감지 및 전염
        for(let i=0; i<users.length; i++) {{
            for(let j=i+1; j<users.length; j++) {{
                if(users[i].mesh.position.distanceTo(users[j].mesh.position) < 1.5) {{
                    if(users[i].infected && !users[j].infected) {{ users[j].infected=true; users[j].mesh.material=redMat; infected_visual_count++; }}
                    if(users[j].infected && !users[i].infected) {{ users[i].infected=true; users[i].mesh.material=redMat; infected_visual_count++; }}
                }}
            }}
        }}
        renderer.render(scene, camera);
    }}

    setupUsers();
    animate();
</script>
</body>
</html>
"""
# 🚀 마지막 components.html의 높이를 850px로 대폭 확장하여 모든 내용이 크게 보이게 함
components.html(combined_embedded_code, height=850, scrolling=False)
