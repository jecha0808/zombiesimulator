import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 시뮬레이션] 내 개인정보가 100만 명에게 퍼지는 시간")
st.markdown("""
교과서 225쪽의 **'디지털 공간에서 정보의 확산 속도'**를 연예인 루머 유포 사례 및 100만 명 규모의 가상 네트워크와 연계한 심화 실습 앱입니다.  
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

# 3. 레이아웃 분할 (좌측: 3D 시뮬레이터 / 우측: 연예인 사례 중심 교육 리포트)
col_sim, col_guide = st.columns([1.2, 0.8])

with col_sim:
    st.subheader("🎮 3D 네트워크 확산 및 궤적 시각화")
    
    # 꼬리 효과(Trail)와 100만 명 스케일링 로직이 추가된 Three.js 스크립트
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
                color: white; font-family: sans-serif; font-size: 15px; font-weight: bold;
                background: rgba(0,0,0,0.8); padding: 12px 24px; border-radius: 20px; text-align: center;
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
    const VISUAL_USERS = 60; // 화면에 그릴 최적의 샘플 공 개수 (렉 방지)
    const MAX_TARGET_USERS = 1000000; // 가상 최대 도달 유저수 (100만 명)
    const BALL_RADIUS = 0.5;
    const sharing_speed = {sharing_speed};
    
    let time_elapsed = 0;
    let infected_visual_count = 1;
    const dt = 0.02;
    
    // Three.js 인프라 세팅
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, 650 / 500, 0.1, 1000);
    camera.position.set(0, 0, 35);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(650, 500);
    container.appendChild(renderer.domElement);
    
    // 조명
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);
    
    // 경계 상자 외곽선
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 2 }})
    );
    scene.add(boxWireframe);
    
    // 공 생성
    const users = [];
    const sphereGeom = new THREE.SphereGeometry(BALL_RADIUS, 16, 16);
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000, emissive: 0x330000, shininess: 50 }});
    
    // 최초 유출자의 이동 궤적(Trail)을 위한 배열 및 라인 설정
    const trailPoints = [];
    const maxTrailLength = 50; // 궤적의 길이
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
    
    // 마우스 카메라 회전 인터페이스 (중괄호 오류 방지 구조 적용)
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
    
    // 메인 애니메이션 루프
    function animate() {{
        requestAnimationFrame(animate);
        
        if (infected_visual_count < VISUAL_USERS) {{
            time_elapsed += dt;
        }}
        
        // 🚀 [수학적 비례 환산 알고리즘]: 샘플 전파 비율을 100만 명 스케일로 확장 계산
        const infectionRatio = infected_visual_count / VISUAL_USERS;
        let scaledInfected = Math.floor(infectionRatio * MAX_TARGET_USERS);
        if (scaledInfected === 0 && infected_visual_count > 0) scaledInfected = 1;
        if (infected_visual_count === VISUAL_USERS) scaledInfected = MAX_TARGET_USERS;
        
        // 실시간 텍스트 출력
        if (scaledInfected < MAX_TARGET_USERS) {{
            infoOverlay.innerHTML = "⏱️ 경과 시간: " + time_elapsed.toFixed(1) + "초<br>🚨 <span style='color:#ff4d4d;'>가상 피해 인구 수: " + scaledInfected.toLocaleString() + "명</span> / 1,000,000명";
        }} else {{
            infoOverlay.innerHTML = "🏁 <span style='color:#ff4d4d; font-size:17px;'>전파 종료: 가상 SNS 유저 1,000,000명 전원 감염</span><br>⏳ 총 확산 소요 시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        // 1. 공 이동 및 상자 벽 충돌 반사
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
        
        // 📌 [최초 유출자 궤적 실시간 기록 파트]
        const firstUserPos = users[0].mesh.position;
        trailPoints.push(new THREE.Vector3(firstUserPos.x, firstUserPos.y, firstUserPos.z));
        if (trailPoints.length > maxTrailLength) {{
            trailPoints.shift();
        }}
        
        // 라인 버퍼 데이터 업데이트
        const positions = trailLine.geometry.attributes.position.array;
        for (let i = 0; i < maxTrailLength; i++) {{
            const pt = trailPoints[i] || firstUserPos;
            positions[i * 3] = pt.x;
            positions[i * 3 + 1] = pt.y;
            positions[i * 3 + 2] = pt.z;
        }}
        trailLine.geometry.attributes.position.needsUpdate = true;
        
        // 2. 구체 간 충돌 및 감염 처리
        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                const u1 = users[i];
                const u2 = users[j];
                const dist = u1.mesh.position.distanceTo(u2.mesh.position);
                
                if (dist < (BALL_RADIUS * 2)) {{
                    if (u1.infected && !u2.infected) {{
                        u2.mesh.material = redMat; u2.infected = true; infected_visual_count++;
                    }} else if (u2.infected && !u1.infected) {{
                        u1.mesh.material = redMat; u1.infected = true; infected_visual_count++;
                    }}
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
    
    components.html(threejs_embed_code, height=520, scrolling=False)

with col_guide:
    st.subheader("💡 대중예술인(연예인)과 정보윤리")
    
    st.error("""
    🎬 **연예인들이 허위 사실과 루머 유포를 극도로 조심해야 하는 이유**
    
    1. **광범위한 노드로 이루어진 3D 초연결성** 연예인은 일반인보다 SNS 네트워크상에서 압도적으로 많은 연결선(팔로워, 구독자)을 가진 '허브(Hub)' 자리에 있습니다. 단 한 명의 유출로 시작된 붉은 선(궤적)이 순식간에 **100만 명의 대중에게 기하급수적으로 사방으로 동시 확산**됩니다.
    
    2. **낙인 효과와 주사위의 불가역성** 시뮬레이션에서 하얀 공이 한 번 빨간색(감염)으로 변하면 다시 하얗게 되돌릴 수 없는 것처럼, 디지털 공간에 한 번 퍼진 루머는 추후 '사실무근'으로 밝혀지더라도 이미 100만 명의 머릿속에 각인되어 주입 이전의 청정한 상태로 복구하는 것이 불가능에 가깝습니다.
    """)
    
    st.markdown("""
    ### 📝 수업 활용 학생 토의 발문
    * **질문 1**: 화면 속 최초 유출자(빨간 공) 뒤에 남는 빨간색 이동 궤적을 관찰해 보세요. 처음 한 사람이 이리저리 돌아다니며 부딪힌 작은 행동이, 나중에 전체 상자를 빨갛게 물들이는 데 어떤 도화선 역할을 했나요?
    * **질문 2**: 정보 공유 속도 슬라이더를 `12` 이상으로 올렸을 때, 100만 명에게 도달하는 시간이 몇 초나 단축되나요? '자극적인 제목'이 정보의 이동 속도를 어떻게 증폭시키는지 연계하여 서술해 봅시다.
    """)

    if st.button("🔄 시뮬레이션 다시 시작하기"):
        st.rerun()
