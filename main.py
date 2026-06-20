import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# 1. 스트림릿 웹 화면 구성 및 페이지 설정
st.set_page_config(
    page_title="정보윤리 3D 시뮬레이터", 
    page_icon="🔒", 
    layout="wide"
)

st.title("🔒 [정보윤리 실습] 2차 네트워크(팔로워의 팔로워) 기반 정보 확산 시뮬레이션")
st.markdown("""
교과서 225쪽 **'디지털 공간의 정보 확산'** 단원 실습 앱입니다.  
내 팔로워가 적어도, **그 친구들의 팔로워(2차 네트워크)**를 통해 얼마나 파괴적으로 정보가 퍼지는지 확인해 보세요.
""")
st.markdown("---")

# 2. 사이드바 인터페이스 구성 (2차 확산 변수 추가)
st.sidebar.header("⚙️ 내 인스타그램 환경 변수 설정")

# 변수 1: 내 팔로워 수 (1차 네트워크)
my_followers = st.sidebar.slider(
    "1. 나의 팔로워 수 (명)", 
    min_value=10, 
    max_value=1000, 
    value=30, 
    step=10
)

# 변수 2: 내 팔로워들의 평균 팔로워 수 (2차 네트워크의 핵심 가중치!)
friends_followers = st.sidebar.slider(
    "2. 내 친구들의 평균 팔로워 수 (명)", 
    min_value=10, 
    max_value=500, 
    value=100, 
    step=10
)

# 변수 3: 내가 올린 스토리 수 (확산 가속도 인자)
story_count = st.sidebar.slider(
    "3. 내가 올린 스토리/게시글 수 (개)", 
    min_value=1, 
    max_value=10, 
    value=2, 
    step=1
)

# 💡 1차와 2차 네트워크를 결합한 총 잠재적 노출 인구 계산
# 중학생 아이들의 실제 겹치는 네트워크를 감안하여 현실적인 필터링 상수를 적용한 총 피해 규모
total_potential_pool = int(my_followers * (1 + (friends_followers * 0.4)))

# 스토리 수와 친구들의 네트워크 크기가 결합된 최종 확산 속도 상수
calculated_speed = story_count * (1 + (friends_followers * 0.01))

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 시각적 가이드**
* 🔴 **빨간 공**: 이미 정보가 유출되어 감염된 유저
* ⚪ **하얀 공**: 아직 노출되지 않은 잠재적 유저
* 🖱️ 3D 화면을 마우스 드래그하면 공간을 돌려볼 수 있습니다.
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
    "얘들아, 우측 그래프의 Y축 최대치를 보렴. 내 팔로워는 분명 30명으로 맞췄는데, 총 피해 인원은 1,000명이 넘어가고 있지? 왜 그럴까? 
    바로 너희 스토리를 본 30명의 친구들에게는 각자 100명씩의 또 다른 친구(팔로워의 팔로워)들이 있기 때문이야. 
    이걸 <b>'네트워크 효과'</b>라고 부른단다. SNS에 올린 게시물은 '우리끼리만' 보는 게 절대 불가능한 구조야."
    """)

# 3. 📊 2차 확산 수학 모델 기반 그래프 생성 (절대 안 사라짐)
st.subheader("📈 1차 + 2차 네트워크 결합 실시간 확산 속도 곡선")

time_steps = [round(x * 0.5, 1) for x in range(0, 31)] # 0초부터 15초까지
infected_data = []

for t in time_steps:
    # 2차 확산은 초반엔 완만하다가 친구의 친구 네트워크를 타는 순간 수직 상승하는 특징을 가짐
    k = 0.2 + (calculated_speed * 0.03)
    mid_point = max(2.5, 9.0 - (calculated_speed * 0.5))
    
    # 로지스틱 수식 적용
    y_val = total_potential_pool / (1 + ((total_potential_pool - 1) * (2.718 ** (-k * (t - mid_point)))))
    infected_data.append(int(y_val))

chart_df = pd.DataFrame({
    "시간 (초)": time_steps,
    "총 피해 유저 수 (명)": infected_data
}).set_index("시간 (초)")

# 메인 레이아웃 분할
col_sim, col_chart = st.columns([1.1, 0.9])

with col_chart:
    st.write(f"📊 **'팔로워의 팔로워'까지 합산된 누적 유출 그래프 (최대 {total_potential_pool:,}명 규모)**")
    st.line_chart(chart_df, height=320)
    
    st.markdown(f"""
    <div style="padding: 12px; background-color: #262626; border-radius: 5px; font-size: 12px; color: #cbd5e1; line-height:1.5;">
        🎯 <b>실험 포인트</b><br>
        • 내 팔로워 수(`1번`)를 <b>{my_followers}명</b>으로 아주 작게 설정해도, 친구들의 팔로워 수(`2번`)를 올리면 총 피해 인원이 기하급수적으로 폭증하는 것을 볼 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

with col_sim:
    st.write("🎮 **3D 확산 가상 시뮬레이터 (공들의 전파 속도 동적 반영)**")
    
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
    const sharing_speed = {calculated_speed}; // 2차 가중치가 반영된 속도
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
