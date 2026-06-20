import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
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
* 🖱️ 3D 화면을 마우스 클릭 후 드래그하면 카메라 각도를 돌려볼 수 있습니다.
""")

# 3. 레이아웃 분할 (좌측: 3D 시뮬레이터 / 우측: 탐구 리포트 및 발문)
col_sim, col_guide = st.columns([1.3, 0.7])

with col_sim:
    st.subheader("🎮 3D 네트워크 확산 가상 공간")
    
    # 스트림릿 내 임베딩을 위해 웹 표준 Three.js 엔진으로 재가공한 3D 시뮬레이터 템플릿
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
                color: white; font-family: sans-serif; font-size: 16px; font-weight: bold;
                background: rgba(0,0,0,0.6); padding: 8px 16px; border-radius: 20px; text-align: center;
                pointer-events: none; width: 80%;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
    <div id="canvas-container">
        <div id="info-overlay">준비 중...</div>
    </div>
    
    <script>
    const container = document.getElementById('canvas-container');
    const infoOverlay = document.getElementById('info-overlay');
    
    // 환경 설정 변수 주입
    const CONTAINER_SIZE = 15;
    const NUM_USERS = {num_users};
    const BALL_RADIUS = 0.5;
    const sharing_speed = {sharing_speed};
    
    let time_elapsed = 0;
    let infected_count = 1;
    const dt = 0.03;
    
    // 3D 씬, 카메라, 렌더러 설정
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, 650 / 500, 0.1, 1000);
    camera.position.set(0, 0, 35);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(650, 500);
    container.appendChild(renderer.domElement);
    
    // 조명 추가
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
    dirLight.position.set(20, 40, 20);
    scene.add(dirLight);
    
    // 외곽 테두리 상자 그리드 생성
    const boxGeom = new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2);
    const edges = new THREE.EdgesGeometry(boxGeom);
    const lineMat = new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 2 }});
    const boxWireframe = new THREE.LineSegments(edges, lineMat);
    scene.add(boxWireframe);
    
    // 공 객체 배열 생성
    const users = [];
    const sphereGeom = new THREE.SphereGeometry(BALL_RADIUS, 16, 16);
    
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff, shininess: 30 }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000, shininess: 30 }});
    
    for (let i = 0; i < NUM_USERS; i++) {{
        const isFirst = (i === 0);
        const mesh = new THREE.Mesh(sphereGeom, isFirst ? redMat : whiteMat);
        
        // 박스 내부 임의 위치 지정
        mesh.position.set(
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1),
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1),
            (Math.random() * (CONTAINER_SIZE * 2 - 2)) - (CONTAINER_SIZE - 1)
        );
        
        scene.add(mesh);
        
        // 이동 방향 무작위 지정
        const dir = new THREE.Vector3(
            (Math.random() * 2) - 1,
            (Math.random() * 2) - 1,
            (Math.random() * 2) - 1
        ).normalize();
        
        users.push({{
            mesh: mesh,
            velocity: dir,
            infected: isFirst
        }});
    }}
    
  // 간단한 마우스 회전 제어 감지
    let isDragging = false;
    let previousMousePosition = {{ x: 0, y: 0 }};
    
    window.addEventListener('mousedown', (e) => {{ isDragging = true; }});
    window.addEventListener('mousemove', (e) => {{
        const deltaMove = {{ x: e.offsetX - previousMousePosition.x, y: e.offsetY - previousMousePosition.y }};
        if (isDragging) {{
            boxWireframe.rotation.y += deltaMove.x * 0.005;
            boxWireframe.rotation.x += deltaMove.y * 0.005;
            users.forEach(u => {{
                // 유저 공들도 상자 회전에 따라 공전 효과 부여
                u.mesh.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), deltaMove.x * 0.005);
                u.mesh.position.applyAxisAngle(new THREE.Vector3(1, 0, 0), deltaMove.x * 0.005);
                u.velocity.applyAxisAngle(new THREE.Vector3(0, 1, 0), deltaMove.x * 0.005);
                u.velocity.applyAxisAngle(new THREE.Vector3(1, 0, 0), deltaMove.x * 0.005);
            }});
        }}
        previousMousePosition = {{ x: e.offsetX, y: e.offsetY }};
    }});
    window.addEventListener('mouseup', (e) => {{ isDragging = false; }}}}); // <- 이 부분의 괄호를 4개(}}}})로 교정했습니다.
    // 메인 프레임 애니메이션 루프
    function animate() {{
        requestAnimationFrame(animate);
        
        if (infected_count < NUM_USERS) {{
            time_elapsed += dt;
        }}
        
        infoOverlay.innerText = "⏳ 걸린 시간: " + time_elapsed.toFixed(1) + "초 | 🔴 감염 계정: " + infected_count + " / " + NUM_USERS + "개";
        
        // 1. 공 이동 및 상자 벽 충돌 반사 연산
        for (let i = 0; i < users.length; i++) {{
            const u = users[i];
            
            // 위치 업데이트 (방향 * 입력 속도 * dt)
            u.mesh.position.x += u.velocity.x * sharing_speed * dt;
            u.mesh.position.y += u.velocity.y * sharing_speed * dt;
            u.mesh.position.z += u.velocity.z * sharing_speed * dt;
            
            const boundary = CONTAINER_SIZE - BALL_RADIUS;
            
            // X축 벽면 바운스
            if (Math.abs(u.mesh.position.x) >= boundary) {{
                u.velocity.x = -u.velocity.x;
                u.mesh.position.x = u.mesh.position.x > 0 ? boundary : -boundary;
            }}
            // Y축 벽면 바운스
            if (Math.abs(u.mesh.position.y) >= boundary) {{
                u.velocity.y = -u.velocity.y;
                u.mesh.position.y = u.mesh.position.y > 0 ? boundary : -boundary;
            }}
            // Z축 벽면 바운스
            if (Math.abs(u.mesh.position.z) >= boundary) {{
                u.velocity.z = -u.velocity.z;
                u.mesh.position.z = u.mesh.position.z > 0 ? boundary : -boundary;
            }}
        }}
        
        // 2. 공들 사이의 충돌체크 및 감염 확산 알고리즘
        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                const u1 = users[i];
                const u2 = users[j];
                
                const dist = u1.mesh.position.distanceTo(u2.mesh.position);
                
                // 두 구체가 물리적으로 교차했을 때 충돌 인정
                if (dist < (BALL_RADIUS * 2)) {{
                    if (u1.infected && !u2.infected) {{
                        u2.mesh.material = redMat;
                        u2.infected = true;
                        infected_count++;
                    }} else if (u2.infected && !u1.infected) {{
                        u1.mesh.material = redMat;
                        u1.infected = true;
                        infected_count++;
                    }}
                }}
            }}
        }}
        
        if (infected_count >= NUM_USERS) {{
            infoOverlay.innerHTML = "🚨 <span style='color:#ff4d4d;'>전원 유출 완료!</span> 총 확산 시간: " + time_elapsed.toFixed(1) + "초";
        }}
        
        renderer.render(scene, camera);
    }}
    
    animate();
    </script>
    </body>
    </html>
    """
    
    # 스트림릿 내부에 안정적인 3D 그래픽 프레임 크기로 인젝션
    components.html(threejs_embed_code, height=520, scrolling=False)

with col_guide:
    st.subheader("💡 수업용 탐구 활동 보고서")
    
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
       * 전 방향(3D)으로 실시간 연결된 디지털 공간의 확산 속도 그래프는 어떤 특징을 보이나요?
    """)

    if st.button("🔄 시뮬레이션 다시 시작하기"):
        st.rerun()
