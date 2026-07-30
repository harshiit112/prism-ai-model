import streamlit as st
import time

from agent_loader import load_agent_components

# Safely import agent modules if available in user's environment
components, import_error = load_agent_components()
build_reader_agent = components["build_reader_agent"]
build_search_agent = components["build_search_agent"]
writer_chain = components["writer_chain"]
critic_chain = components["critic_chain"]

if import_error is not None:
    st.session_state.setdefault("agent_import_error", str(import_error))

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PrismAIModel · Next-Gen AI Research",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if import_error is not None:
    st.warning(
        "Agent components could not be loaded. The app will show a friendly fallback message until the environment is fixed."
    )

# ── Custom CSS & Enhanced Three.js 3D Background Canvas ────────────────────────
st.markdown("""
<!-- Three.js & Orbit Controls / Math Libraries -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<!-- Ambient Mouse Tracking Glow Overlay -->
<div id="cursor-glow"></div>

<!-- Canvas for 3D Interactive Scene -->
<canvas id="bg-3d-canvas"></canvas>

<script>
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('bg-3d-canvas');
    if (!canvas) return;

    // ── Scene Setup ──
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 4.5;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // ── Outer Deformable Wireframe Geometry ──
    const outerGeo = new THREE.IcosahedronGeometry(2.4, 3);
    const posAttribute = outerGeo.attributes.position;
    const originalPositions = posAttribute.array.slice();

    const outerMat = new THREE.MeshBasicMaterial({
        color: 0x88bbff,
        wireframe: true,
        transparent: true,
        opacity: 0.18
    });
    const outerSphere = new THREE.Mesh(outerGeo, outerMat);
    scene.add(outerSphere);

    // ── Inner Cyber Core (Floating Octahedron) ──
    const innerGeo = new THREE.OctahedronGeometry(1.1, 0);
    const innerMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        wireframe: true,
        transparent: true,
        opacity: 0.35
    });
    const innerCore = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerCore);

    // ── Quantum Cloud Particles ──
    const particleGeo = new THREE.DodecahedronGeometry(1.8, 2);
    const particleMat = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.025,
        transparent: true,
        opacity: 0.5,
        blending: THREE.AdditiveBlending
    });
    const particleCloud = new THREE.Points(particleGeo, particleMat);
    scene.add(particleCloud);

    // ── Mouse & Interactivity Tracking ──
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;
    const cursorGlow = document.getElementById('cursor-glow');

    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.0008;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.0008;

        // Custom Cursor Spotlight Position Update
        if (cursorGlow) {
            cursorGlow.style.left = e.clientX + 'px';
            cursorGlow.style.top = e.clientY + 'px';
        }
    });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // ── Animation Loop with Mesh Distortion ──
    let clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const time = clock.getElapsedTime();

        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;

        // Dynamic Rotations
        outerSphere.rotation.y = time * 0.15 + targetX * 2;
        outerSphere.rotation.x = time * 0.08 + targetY * 2;

        innerCore.rotation.y = -time * 0.3;
        innerCore.rotation.z = time * 0.2;

        particleCloud.rotation.y = -time * 0.1 + targetX;
        particleCloud.rotation.x = time * 0.05 + targetY;

        // Dynamic Wave Deformation on Outer Wireframe
        const position = outerGeo.attributes.position;
        for (let i = 0; i < position.count; i++) {
            const u = originalPositions[i * 3];
            const v = originalPositions[i * 3 + 1];
            const w = originalPositions[i * 3 + 2];

            const wave = Math.sin(time * 3 + u * 2 + v * 2) * 0.06;
            position.setXYZ(i, u + u * wave * 0.3, v + v * wave * 0.3, w + w * wave * 0.3);
        }
        outerGeo.attributes.position.needsUpdate = true;

        renderer.render(scene, camera);
    }
    animate();
});
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Interactive Cursor Glow Spotlight ── */
#cursor-glow {
    position: fixed;
    top: 0;
    left: 0;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.06) 0%, rgba(0, 240, 255, 0.03) 40%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    transform: translate(-50%, -50%);
    z-index: 0;
    transition: width 0.3s, height 0.3s;
    mix-blend-mode: screen;
}

/* ── Fixed 3D Canvas Styling ── */
#bg-3d-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
    opacity: 0.65;
}

/* ── Keyframe Animations ── */
@keyframes ambientGlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pulseBorder {
    0% { border-color: rgba(255, 255, 255, 0.2); box-shadow: 0 0 10px rgba(255, 255, 255, 0.05); }
    50% { border-color: rgba(255, 255, 255, 0.8); box-shadow: 0 0 25px rgba(255, 255, 255, 0.25); }
    100% { border-color: rgba(255, 255, 255, 0.2); box-shadow: 0 0 10px rgba(255, 255, 255, 0.05); }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* ── Reset & Base Layout ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

.stApp {
    background: #030305;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.1) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 100%, rgba(0, 180, 255, 0.05) 0%, transparent 70%),
        radial-gradient(ellipse 100% 100% at 50% 50%, transparent 40%, rgba(0, 0, 0, 0.9) 100%);
    background-size: 200% 200%;
    animation: ambientGlow 15s ease infinite;
}

/* ── Hide Default Streamlit Layout Elements ── */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; height: 0; }
[data-testid="stHeader"] { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

.block-container { 
    padding-top: 0.5rem !important; 
    padding-bottom: 4rem; 
    padding-left: 3rem; 
    padding-right: 3rem; 
    max-width: 1200px;
    position: relative;
    z-index: 1;
}

/* ── Compact Hero Header with Shimmer Effect ── */
.hero {
    text-align: center;
    padding: 1.5rem 0 1rem;
    position: relative;
    animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #a1a1aa;
    margin-bottom: 0.4rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 5vw, 4.4rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin: 0 0 0.5rem;
    text-shadow: 0 0 30px rgba(255, 255, 255, 0.15);
}
.hero h1 span {
    color: #71717a;
    transition: all 0.5s ease;
}
.hero h1:hover span {
    color: #ffffff;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
}
.hero-sub {
    font-size: 0.98rem;
    font-weight: 300;
    color: #8e8e93;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.5;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
    margin: 1.2rem 0;
}

/* ── Futuristic Hover Input Card ── */
.input-card {
    background: rgba(14, 14, 18, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeInUp 0.9s ease-out;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
.input-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
}
.input-card:hover::before { opacity: 1; }
.input-card:hover {
    transform: translateY(-4px) scale(1.005);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8), 0 0 30px rgba(255, 255, 255, 0.1);
}

/* ── Streamlit Input Overrides with Glowing Focus ── */
.stTextInput > div > div > input {
    background: rgba(8, 8, 10, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:hover {
    border-color: rgba(255, 255, 255, 0.4) !important;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.08) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ffffff !important;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.25) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #e4e4e7 !important;
    font-weight: 500 !important;
}

/* ── High-Tech Cyber Button ── */
.stButton > button {
    background: #ffffff !important;
    color: #000000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    border: 1px solid #ffffff !important;
    border-radius: 12px !important;
    padding: 0.8rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 20px rgba(255, 255, 255, 0.15) !important;
    width: 100%;
}
.stButton > button:hover {
    background: #09090b !important;
    color: #ffffff !important;
    border-color: #ffffff !important;
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.3), 0 0 15px rgba(255, 255, 255, 0.2) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── Interactive Example Tags Hover ── */
.example-chip {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.75rem;
    color: #a1a1aa;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.example-chip:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.6);
    color: #ffffff;
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 5px 15px rgba(255, 255, 255, 0.15);
}

/* ── Pipeline Step Cards ── */
.step-card {
    background: rgba(14, 14, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeInUp 1s ease-out;
}
.step-card:hover {
    transform: translateX(6px) scale(1.01);
    border-color: rgba(255, 255, 255, 0.35);
    background: rgba(25, 25, 35, 0.85);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
}
.step-card.active {
    border-color: #ffffff;
    background: rgba(255, 255, 255, 0.06);
    animation: pulseBorder 2s infinite ease-in-out;
}
.step-card.done {
    border-color: rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.02);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255, 255, 255, 0.08);
    transition: background 0.3s;
}
.step-card.active::before { background: #ffffff; box-shadow: 0 0 10px #ffffff; }
.step-card.done::before   { background: #a1a1aa; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.2rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #a1a1aa;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
}
.status-waiting  { color: #52525b; }
.status-running  { color: #ffffff; text-shadow: 0 0 8px rgba(255, 255, 255, 0.8); }
.status-done     { color: #a1a1aa; }

/* ── Result Panels with Glow Hover ── */
.result-panel {
    background: rgba(12, 12, 15, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    transition: all 0.35s ease;
    animation: fadeInUp 0.5s ease-out;
}
.result-panel:hover {
    border-color: rgba(255, 255, 255, 0.35);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 255, 255, 0.05);
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ffffff;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #d4d4d8;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & Feedback Panels ── */
.report-panel {
    background: rgba(14, 14, 18, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    backdrop-filter: blur(16px);
    transition: all 0.35s ease;
    animation: fadeInUp 0.6s ease-out;
}
.report-panel:hover {
    border-color: #ffffff;
    box-shadow: 0 15px 40px rgba(255, 255, 255, 0.08);
}
.feedback-panel {
    background: rgba(12, 12, 15, 0.85);
    border: 1px solid rgba(161, 161, 170, 0.25);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    backdrop-filter: blur(16px);
    transition: all 0.35s ease;
    animation: fadeInUp 0.6s ease-out;
}
.feedback-panel:hover {
    border-color: #a1a1aa;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange {
    color: #ffffff;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}
.panel-label.green {
    color: #a1a1aa;
    border-bottom: 1px solid rgba(161, 161, 170, 0.2);
}

/* ── Progress Indicator ── */
.stSpinner > div { color: #ffffff !important; }

/* ── Expander Hover ── */
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #a1a1aa !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
    transition: all 0.25s ease !important;
}
details summary:hover {
    color: #ffffff !important;
}

/* ── Section Heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
    margin: 1rem 0 0.8rem;
}

/* ── Notice Footer ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #52525b;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#71717a;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>PrismAI<span>Model</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: Input Left, Pipeline Right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2026",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips with hover styling
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#52525b;letter-spacing:0.1em;align-self:center;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2026", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span class="example-chip">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        if step in r:
            return "done"
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    if import_error is not None or None in (build_search_agent, build_reader_agent, writer_chain, critic_chain):
        st.session_state.running = False
        st.session_state.done = True
        st.error("The research pipeline could not start because the agent components are unavailable in this environment.")
        st.stop()

    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    PrismAIModel · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)