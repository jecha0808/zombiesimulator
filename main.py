import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 시뮬레이션] 내 개인정보가 100만 명에게 퍼지는 시간")
st.markdown("""
교과서의 **'디지털 공간에서 정보의 확산 속도'**를 연예인 루머 유포 사례 및 100만 명 규모의 가상 네트워크와 연계한 심화 실습 앱입니다.  
왼쪽 사이드바에서 **공유 속도(파급력)**를 조절하며, 단 하나의 최초 유출 궤적이 어떻게 기하급수적인 대재앙으로 이어지는지 관찰해 보세요.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성 (학생 조작 포인트)
st.sidebar.header("⚙️ 디지털 파급력 설정")

sharing_speed = st.sidebar.slider(
    "1. 정보의 자극성 및 공유 속도", 
    min_value=1, 
    max_value=15, 
    value=5, 
    step=1
)

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **궤적이 남는 빨간 공**: 최초 유출자 (연예인 루머/개인정보 최초 게시물)
* ⚪ **하얀 공**: 일반 대중 및 SNS 유저 (전파 매개체)
* 🖱️ 3D 화면을 마우스 클릭 후 드래그하면 카메라 각도를 돌려볼 수 있습니다.
""")

# 3. 실시간 그래프 출력을 위한 스트림릿 세션 상태(Session State) 초기화
if "chart_data" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=["시간(초)", "피해 유저 수(명)"]).set_index("시간(초)")

# 4. 레이아웃 분할 (좌측: 3D 시뮬레이터 / 우측: 실시간 그래프 및 교육 리포트)
col_sim, col_chart = st.columns([1.1, 0.9])

with col_sim:
    st.subheader("🎮 3D 네트워크 확산 및 궤적 시각화")
    
    # [시각화 연동] 자바스크립트에서 계산된 확산 데이터를 스트림릿 세션이나 부모 창으로 전달할 수 있도록 구성된 Three.js 스크립트
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
    const MAX_TARGET_USERS = 1000000; 
    const BALL_RADIUS = 0.5;
    const sharing_speed = {sharing_speed};
    
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
            infoOverlay.innerHTML = "⏱️ 경과 시간: " + time_elapsed.toFixed(1) + "초<br>🚨 <span style='color:#ff4d4d;'>가상 피해 인구 수: " + scaledInfected.toLocaleString() + "명</span> / 1,000,000명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d; font-size:16px;'>전파 종료: 가상 SNS 유저 1,000,000명 전원 감염</span><br>⏳ 총 확산 소요 시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        // 부모 스트림릿 창으로 실시간 데이터 전송 (0.2초 간격 렌더링 스로틀링)
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

# 5. 자바스크립트가 보내온 실시간 데이터를 파이썬 Pandas DataFrame에 축적하는 컴포넌트 라이더
import json
from streamlit_js_eval import streamlit_js_eval

# 자바스크립트의 postMessage를 수신하기 위한 더미 웹 컴포넌트 리스너 설정
st_components_listener = f"""
<script>
window.addEventListener("message", (event) => {{
    if (event.data && event.data.type === "streamlit_zombie_update") {{
        const data = event.data;
        // 스트림릿 백엔드가 인식 가능한 보이지 않는 입력창에 값 주입
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

# 실시간 스트림릿 데이터 축적 연동용 세션 핸들링 공간
with col_chart:
    st.subheader("📈 실시간 정보 확산 속도 곡선 (100만 명 기준)")
    
    # 3D 가상 공간 데이터를 받아오기 위한 데이터 링커 헬퍼 설정
    data_carrier = st.text_input("data_bridge", value="", key="zombie_data_bridge", label_visibility="collapsed")
    
    if data_carrier:
        try:
            t_val, inf_val = data_carrier.split(",")
            t_val = float(t_val)
            inf_val = int(inf_val)
            
            # 기존 데이터프레임에 실시간 스냅샷 추가
            if t_val not in st.session_state.chart_data.index:
                new_row = pd.DataFrame([[inf_val]], columns=["피해 유저 수(명)"], index=[t_val])
                st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_row])
        except:
            pass

    # 📊 실시간 스트림릿 차트 그리기
    if not st.session_state.chart_data.empty:
        st.line_chart(st.session_state.chart_data, height=300)
    else:
        st.info("시뮬레이션이 시작되면 이곳에 실시간 확산 속도 그래프가 그려집니다.")

    st.subheader("💡 대중예술인(연예인)과 정보윤리")
    st.error("""
    🎬 **왜 초반보다 중반 이후에 속도가 무섭게 빨라질까요?**
    
    그래프를 보면 알 수 있듯이, 초반(1~5초)에는 피해자 수가 완만하게 증가합니다. 그러나 감염된 매개체(빨간 공)들이 많아지는 시점부터는 사방에서 동시다발적 접촉이 일어나며 **그래프 기울기가 수직에 가깝게 폭발적으로 상승(기하급수적 증가)**합니다. 
    
    연예인 악성 루머가 단 몇 분 만에 온 인터넷을 도배하고 100만 명에게 도달하는 물리적 이유가 바로 이 그래프의 '기울기 급변 폭발 구간' 때문입니다.
    """)
    
    if st.button("🔄 시뮬레이션 및 그래프 리셋"):
        st.session_state.chart_data = pd.DataFrame(columns=["시간(초)", "피해 유저 수(명)"]).set_index("시간(초)")
        st.rerun()
