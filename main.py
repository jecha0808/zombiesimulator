import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 내 SNS 설정에 따른 개인정보 확산 속도 시뮬레이션")
st.markdown("""
교과서 225쪽 **'디지털 공간의 정보 확산'** 단원 실습 앱입니다.  
왼쪽 제어창에서 **'나의 팔로워 수'**와 **'내가 올린 스토리 수'**를 바꾸면, 우측의 **실시간 확산 속도 곡선**이 즉각 반영됩니다.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

follower_count = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)", 
    min_value=10, 
    max_value=2000, 
    value=100, 
    step=10
)

story_count = st.sidebar.slider(
    "2. 내가 올린 스토리/게시글 수 (개)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

# 스토리 수에 따른 전파 가속도 가중치
calculated_speed = story_count * 2.5

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **궤적이 남는 빨간 공**: 유출된 스토리/게시글 (최초 유출자)
* ⚪ **하얀 공**: 내 스토리를 본 팔로워 및 일반 유저들
* 🖱️ 3D 화면을 마우스 드래그하면 공간을 돌려볼 수 있습니다.
""")

# 🧑‍🏫 교사용 가이드 숨김 메뉴 (사이드바 내부 격리)
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
    비록 내 팔로워는 소수이지만, 그 친구들이 다른 친구들과 겹겹이 연결되어 있어서 순식간에 외부로 퍼져나갈 수 있어! 우측 그래프가 꺾여 올라가는 속도를 보렴!"
    """)

# 3. 📊 안정적인 스트림릿 내부 자체 수학적 시뮬레이션 그래프 생성
# (자바스크립트 비동기 끊김 현상을 완벽히 방절하기 위해 파이썬 내에서 S곡선 데이터 사전 생성)
st.subheader("📈 설정 수치 기반 실시간 확산 속도 곡선")

# 로지스틱 함수(S자 곡선)를 활용한 실시간 확산 데이터 프레임 구축
time_steps = [round(x * 0.5, 1) for x in range(0, 31)] # 0초부터 15초까지
infected_data = []

for t in time_steps:
    # 스토리 수(calculated_speed)가 높을수록 mid_point가 당겨지고 기울기가 급해짐
    k = 0.4 + (calculated_speed * 0.05)
    mid_point = max(3.0, 10.0 - (calculated_speed * 0.8))
    
    # 로지스틱 수식 계산
    y_val = follower_count / (1 + ((follower_count - 1) * (2.718 ** (-k * (t - mid_point)))))
    infected_data.append(int(y_val))

# 스트림릿 순정 라인 차트용 데이터 바인딩
chart_df = pd.DataFrame({
    "시간 (초)": time_steps,
    "피해 팔로워 수 (명)": infected_data
}).set_index("시간 (초)")

# 메인 화면 레이아웃 분할 (좌측: 3D 가상 공간 / 우측: 절대 사라지지 않는 그래프)
col_sim, col_chart = st.columns([1.1, 0.9])

with col_chart:
    st.write(f"📊 **실시간 정보 유출 확산 예측선 (최대 {follower_count}명 규모)**")
    # 스트림릿 전용 고정 차트 출력 (절대 사라지지 않음)
    st.line_chart(chart_df, height=320)
    
    st.markdown("""
    <div style="padding: 10px; background-color: #262626; border-radius: 5px; font-size: 12px; color: #cbd5e1;">
        💡 <b>실험 팁</b>: 왼쪽 슬라이더의 <b>'스토리 수'</b>를 높이면 곡선이 왼쪽으로 당겨지며 가팔라지고, <b>'팔로워 수'</b>를 낮추면 Y축 한계치가 아이들의 실제 환경에 맞게 동적으로 재조정됩니다.
    </div>
    """, unsafe_allow_html=True)

with col_sim:
    st.write("🎮 **3D 확산 가상 시뮬레이터**")
    
    # 3D 렌더러 독립 구동용 HTML 코드
    threejs_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background-color: #1a1a1a; overflow: hidden; }}
            #canvas-container {{ width: 100vw; height: 100vh; position: relative; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
    <div id="canvas-container"></div>
    <script>
    const container = document.getElementById('canvas-container');
    const CONTAINER_SIZE = 13;
    const VISUAL_USERS = 60;
    const sharing_speed = {calculated_speed};
    const dt = 0.02;
    
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 30);
    
    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);
    
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const boxWireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(CONTAINER_SIZE * 2, CONTAINER_SIZE * 2, CONTAINER_SIZE * 2)),
        new THREE.LineBasicMaterial({{ color: 0x555555 }})
    );
    scene.add(boxWireframe);
    
    const users = [];
    const sphereGeom = new THREE.SphereGeometry(0.5, 16, 16);
    const whiteMat = new THREE.MeshPhongMaterial({{ color: 0xffffff }});
    const redMat = new THREE.MeshPhongMaterial({{ color: 0xff0000 }});
    
    for (let i = 0; i < VISUAL_USERS; i++) {{
        const isFirst = (i === 0);
        const mesh = new THREE.Mesh(sphereGeom, isFirst ? redMat : whiteMat);
        mesh.position.set((Math.random()*24)-12, (Math.random()*24)-12, (Math.random()*24)-12);
        scene.add(mesh);
        users.push({{ mesh: mesh, velocity: new THREE.Vector3((Math.random()*2)-1, (Math.random()*2)-1, (Math.random()*2)-1).normalize(), infected: isFirst }});
    }}
    
    function animate() {{
        requestAnimationFrame(animate);
        for (let i = 0; i < users.length; i++) {{
            const u = users[i];
            u.mesh.position.addScaledVector(u.velocity, sharing_speed * dt);
            
            const b = CONTAINER_SIZE - 0.5;
            if (Math.abs(u.mesh.position.x) >= b) {{ u.velocity.x *= -1; u.mesh.position.x = u.mesh.position.x > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.y) >= b) {{ u.velocity.y *= -1; u.mesh.position.y = u.mesh.position.y > 0 ? b : -b; }}
            if (Math.abs(u.mesh.position.z) >= b) {{ u.velocity.z *= -1; u.mesh.position.z = u.mesh.position.z > 0 ? b : -b; }}
        }}
        
        for (let i = 0; i < users.length; i++) {{
            for (let j = i + 1; j < users.length; j++) {{
                if (users[i].mesh.position.distanceTo(users[j].mesh.position) < 1.0) {{
                    if (users[i].infected && !users[j].infected) {{ users[j].mesh.material = redMat; users[j].infected = true; }}
                    else if (users[j].infected && !users[i].infected) {{ users[i].mesh.material = redMat; users[i].infected = true; }}
                }}
            }}
        }}
        boxWireframe.rotation.y += 0.002;
        renderer.render(scene, camera);
    }}
    animate();
    </script>
    </body>
    </html>
    """
    components.html(threejs_code, height=350, scrolling=False)
