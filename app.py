"""
app.py — Premium Smart Shopping Agent UI.
Glassmorphism dark theme with ambient gradient blobs and refined cards.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Shopping Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════
#  PREMIUM CSS
# ═══════════════════════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root tokens ── */
:root {
    --bg: #000000;
    --surface: rgba(255,255,255,0.03);
    --surface-hover: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.08);
    --border-hover: rgba(100,220,255,0.25);
    --text-primary: #eef0f6;
    --text-secondary: #8b8fa3;
    --text-muted: #585c6e;
    --accent: #64dcff;
    --accent-dim: rgba(100,220,255,0.15);
    --green: #5dfea0;
    --yellow: #ffd55e;
    --red: #ff6b6b;
}

/* ── Full-page background ── */
.stApp {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
header, footer, #MainMenu { visibility: hidden !important; }
.block-container { padding-top: 0 !important; max-width: 960px; }

/* ── Ambient gradient blobs (behind everything) ── */
.ambient {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0; overflow: hidden;
}
.blob {
    position: absolute; border-radius: 50%;
    filter: blur(120px); opacity: 0.35;
}
.blob-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, #0a1f33, transparent);
    top: -10%; left: -8%;
    animation: drift1 20s ease-in-out infinite alternate;
}
.blob-2 {
    width: 400px; height: 400px;
    background: radial-gradient(circle, #091a2a, transparent);
    bottom: -5%; right: -5%;
    animation: drift2 25s ease-in-out infinite alternate;
}
.blob-3 {
    width: 300px; height: 300px;
    background: radial-gradient(circle, #061120, transparent);
    top: 40%; left: 50%;
    animation: drift3 18s ease-in-out infinite alternate;
}
@keyframes drift1 { to { transform: translate(60px, 40px); } }
@keyframes drift2 { to { transform: translate(-50px, -30px); } }
@keyframes drift3 { to { transform: translate(-40px, 50px); } }

/* ── Hero section ── */
.hero {
    text-align: center;
    padding: 10px 0 20px;
    position: relative;
    z-index: 1;
}
.hero-label {
    font-size: 0.8rem;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 12px;
    font-weight: 500;
}
.hero-title {
    font-size: 4rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 14px;
    text-shadow: 0 0 30px rgba(100,220,255,0.2);
}
.hero-sub {
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 300;
    max-width: 540px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ══════════════════════════════════════════ */
/*  JARVIS ARC REACTOR — Full HUD            */
/* ══════════════════════════════════════════ */
.orb-wrap { display: flex; justify-content: center; margin: 10px 0 20px; position: relative; z-index: 1; transform: scale(0.9); }
.orb-box { position: relative; width: 340px; height: 340px; }

/* — Ambient halo — */
.orb-halo {
    position: absolute; inset: -60px; margin: auto;
    width: 460px; height: 460px; border-radius: 50%;
    background: radial-gradient(circle, rgba(100,220,255,0.1) 0%, rgba(100,220,255,0.03) 40%, transparent 70%);
    animation: haloPulse 5s ease-in-out infinite;
}
@keyframes haloPulse {
    0%,100% { opacity: 0.5; transform: scale(1); }
    50%     { opacity: 1;   transform: scale(1.06); }
}

/* — Core — */
.orb-core {
    position: absolute; inset: 0; margin: auto;
    width: 64px; height: 64px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #ffffff, #88eaff 40%, #0088aa);
    box-shadow:
        0 0 30px rgba(100,220,255,1),
        0 0 80px rgba(100,220,255,0.6),
        0 0 150px rgba(100,220,255,0.3),
        inset 0 0 20px rgba(255,255,255,0.6);
    animation: coreBreathe 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s;
}
.orb-core::before {
    content: ''; position: absolute; inset: -14px; border-radius: 50%;
    border: 3px solid rgba(100,220,255,0.4);
    animation: coreBreathe 3s ease-in-out infinite 0.5s;
}
.orb-core::after {
    content: ''; position: absolute; inset: -28px; border-radius: 50%;
    border: 1px dashed rgba(100,220,255,0.2);
}
@keyframes coreBreathe {
    0%,100% { transform: scale(1); box-shadow: 0 0 30px rgba(100,220,255,1), 0 0 80px rgba(100,220,255,0.6), 0 0 150px rgba(100,220,255,0.3); }
    50%     { transform: scale(1.15); box-shadow: 0 0 50px rgba(100,220,255,1), 0 0 100px rgba(100,220,255,0.8), 0 0 200px rgba(100,220,255,0.4); }
}

/* — Shared ring base — */
.rng { position: absolute; inset: 0; margin: auto; border-radius: 50%; }

/* Ring 1 — tight inner */
.rng-1 { width: 100px; height: 100px; border: 1.5px solid rgba(100,220,255,0.3); animation: sp 7s linear infinite; }
/* Ring 2 — partial bright arc */
.rng-2 {
    width: 130px; height: 130px;
    border: 2px solid transparent;
    border-top-color: rgba(100,220,255,0.6);
    border-right-color: rgba(100,220,255,0.15);
    animation: sp 5s linear infinite reverse;
}
/* Ring 3 — dashed */
.rng-3 { width: 165px; height: 165px; border: 1px dashed rgba(100,220,255,0.12); animation: sp 18s linear infinite; }
/* Ring 4 — double-arc */
.rng-4 {
    width: 200px; height: 200px;
    border: 2px solid transparent;
    border-top-color: rgba(100,220,255,0.35);
    border-bottom-color: rgba(100,220,255,0.15);
    animation: sp 9s linear infinite reverse;
}
/* Ring 5 — HUD tick marks via conic-gradient */
.rng-5 {
    width: 240px; height: 240px;
    border: 1px solid rgba(100,220,255,0.06);
    background: conic-gradient(
        rgba(100,220,255,0.12) 0deg 2deg, transparent 2deg 30deg,
        rgba(100,220,255,0.08) 30deg 32deg, transparent 32deg 60deg,
        rgba(100,220,255,0.12) 60deg 62deg, transparent 62deg 90deg,
        rgba(100,220,255,0.08) 90deg 92deg, transparent 92deg 120deg,
        rgba(100,220,255,0.12) 120deg 122deg, transparent 122deg 150deg,
        rgba(100,220,255,0.08) 150deg 152deg, transparent 152deg 180deg,
        rgba(100,220,255,0.12) 180deg 182deg, transparent 182deg 210deg,
        rgba(100,220,255,0.08) 210deg 212deg, transparent 212deg 240deg,
        rgba(100,220,255,0.12) 240deg 242deg, transparent 242deg 270deg,
        rgba(100,220,255,0.08) 270deg 272deg, transparent 272deg 300deg,
        rgba(100,220,255,0.12) 300deg 302deg, transparent 302deg 330deg,
        rgba(100,220,255,0.08) 330deg 332deg, transparent 332deg 360deg
    );
    -webkit-mask: radial-gradient(transparent 113px, #000 114px, #000 119px, transparent 120px);
            mask: radial-gradient(transparent 113px, #000 114px, #000 119px, transparent 120px);
    animation: sp 25s linear infinite;
}
/* Ring 6 — green accent arc */
.rng-6 {
    width: 270px; height: 270px;
    border: 2px solid transparent;
    border-left-color: rgba(93,254,160,0.25);
    border-bottom-color: rgba(93,254,160,0.08);
    animation: sp 14s linear infinite reverse;
}
/* Ring 7 — wide outer */
.rng-7 {
    width: 305px; height: 305px;
    border: 1px solid rgba(100,220,255,0.05);
    border-top-color: rgba(100,220,255,0.18);
    animation: sp 22s linear infinite;
}
/* Ring 8 — outermost dotted */
.rng-8 { width: 336px; height: 336px; border: 1px dotted rgba(100,220,255,0.04); animation: sp 40s linear infinite reverse; }

/* — Scan line — rotating beam of light */
.scan {
    position: absolute; inset: 0; margin: auto;
    width: 200px; height: 200px; border-radius: 50%;
    background: conic-gradient(from 0deg, transparent 0deg, rgba(100,220,255,0.08) 30deg, transparent 60deg);
    animation: sp 6s linear infinite;
}

/* — Particle nodes — */
.nd { position: absolute; border-radius: 50%; background: var(--accent); }
.nd-lg { width: 5px; height: 5px; box-shadow: 0 0 8px rgba(100,220,255,0.9), 0 0 16px rgba(100,220,255,0.3); }
.nd-sm { width: 3px; height: 3px; box-shadow: 0 0 5px rgba(100,220,255,0.7); }
.nd-1 { top: 50px;  left: 165px; animation: sp 5s linear infinite;         transform-origin: 5px 120px; }
.nd-2 { top: 170px; left: 30px;  animation: sp 9s linear infinite reverse;  transform-origin: 140px 0px; }
.nd-3 { top: 280px; left: 180px; animation: sp 14s linear infinite;         transform-origin: -10px -110px; }
.nd-4 { top: 100px; right: 25px; animation: sp 7s linear infinite reverse;  transform-origin: -130px 70px; }
.nd-5 { top: 20px;  left: 100px; animation: sp 11s linear infinite;         transform-origin: 70px 150px; }
.nd-6 { bottom: 30px; right: 100px; animation: sp 16s linear infinite reverse; transform-origin: -50px -120px; }

@keyframes sp { to { transform: rotate(360deg); } }

/* — Mic & Listening State — */
.mic-icon {
    color: white;
    z-index: 2;
    transition: all 0.3s;
}
.orb-wrap.listening .orb-core {
    box-shadow: 0 0 50px rgba(100,220,255,1), 0 0 100px rgba(100,220,255,0.8), 0 0 200px rgba(100,220,255,0.6) !important;
    animation: corePulse 0.5s ease-in-out infinite alternate !important;
}
.orb-wrap.listening .mic-icon {
    color: #ff3366 !important;
    filter: drop-shadow(0 0 8px rgba(255,51,102,0.8));
    transform: scale(1.1);
}
@keyframes corePulse {
    0% { transform: scale(1.1); }
    100% { transform: scale(1.25); }
}
.orb-wrap.listening .rng-1 { animation-duration: 2s !important; }
.orb-wrap.listening .rng-2 { animation-duration: 1.5s !important; }
.orb-wrap.listening .rng-3 { animation-duration: 4s !important; }
.orb-wrap.listening .rng-4 { animation-duration: 2.5s !important; }
.orb-wrap.listening .rng-5 { animation-duration: 6s !important; }
.orb-wrap.listening .rng-6 { animation-duration: 3.5s !important; }
.orb-wrap.listening .rng-7 { animation-duration: 5s !important; }
.orb-wrap.listening .rng-8 { animation-duration: 10s !important; }
.orb-wrap.listening .scan { animation-duration: 1.5s !important; }

/* ── Glass input wrapper directly targeting Streamlit container ── */
div[data-testid="stTextInput"] {
    background: var(--surface);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 8px 12px;
    margin-bottom: 6px;
    position: relative; z-index: 1;
    height: 64px;
    display: flex;
    align-items: center;
}
div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}
div[data-testid="stTextInput"] label { color: var(--text-secondary) !important; font-size: 0.85rem !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; margin-bottom: 8px !important; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(100,220,255,0.15), rgba(100,220,255,0.05)) !important;
    border: 1px solid rgba(100,220,255,0.25) !important;
    color: var(--accent) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 12px 28px !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(100,220,255,0.25), rgba(100,220,255,0.1)) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 4px 20px rgba(100,220,255,0.15) !important;
    transform: translateY(-1px) !important;
}

/* ── Product card ── */
@keyframes fadeIn {
    to { opacity: 1; transform: translateY(0); }
}

.p-card {
    background: #0d1a1f;
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    position: relative;
    transition: box-shadow 0.2s ease;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    animation: fadeIn 0.4s ease forwards;
    opacity: 0;
    transform: translateY(5px);
}
.p-card:hover {
    box-shadow: 0 0 15px rgba(100,220,255,0.08);
}
/* Thumbnail */
.p-img-wrap {
    flex-shrink: 0;
    width: 100px; height: 100px;
    background: white;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
}
.p-img-wrap img { width: 90%; height: 90%; object-fit: contain; }

/* Content Wrapper */
.p-content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }

/* Rank Badge */
.p-rank {
    position: absolute; top: 12px; right: 16px;
    font-size: 0.75rem; font-weight: 600;
    color: var(--accent);
    background: rgba(0,0,0,0.4);
    padding: 2px 8px; border-radius: 4px;
    border: 1px solid rgba(100,220,255,0.2);
}

/* Header Row */
.p-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 2px;
    padding-right: 40px; /* space for rank */
}

.p-name {
    font-size: 1rem; font-weight: 600;
    color: #ffffff;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.p-name a { color: inherit; text-decoration: none; }
.p-name a:hover { text-decoration: underline; }

.p-desc {
    font-size: 0.8rem;
    color: #8b8fa3;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 4px;
}

/* Price and Source */
.p-price-row {
    display: flex; align-items: center; gap: 10px;
}
.p-price {
    font-size: 1.3rem; font-weight: 700;
    color: var(--accent);
}
.p-source {
    display: inline-flex; align-items: center;
    padding: 2px 8px; border-radius: 4px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
}
.src-logo { height: 12px; object-fit: contain; }

/* Rating & Auth */
.p-meta-row {
    display: flex; align-items: center; gap: 12px;
    flex-wrap: wrap;
}
.p-rating {
    font-size: 0.8rem;
    color: var(--text-secondary);
}
.p-rating .stars { color: var(--yellow); letter-spacing: 1px; }
.p-rating strong { color: var(--text-primary); font-weight: 600; }

.auth {
    display: inline-block; padding: 2px 8px;
    border-radius: 4px; font-size: 0.7rem; font-weight: 500;
    background: transparent;
}
.auth-hi  { color: var(--green); border: 1px solid var(--green); }
.auth-ok  { color: var(--yellow); border: 1px solid var(--yellow); }
.auth-lo  { color: var(--red); border: 1px solid var(--red); }

/* Specs */
.specs { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    color: #a0a4b8;
    padding: 2px 8px; border-radius: 4px;
    font-size: 0.7rem; font-weight: 500;
}

/* Bottom Row */
.p-bottom-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 6px;
    padding-top: 10px;
    border-top: 1px solid rgba(255,255,255,0.05);
}

.score-wrap {
    display: flex; align-items: center; gap: 10px;
    flex: 1;
    max-width: 250px;
}
.score-lbl { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.bar-bg {
    flex: 1; height: 3px; background: rgba(255,255,255,0.1);
    border-radius: 2px; overflow: hidden;
}
.bar-fill {
    height: 100%; border-radius: 2px;
    background: var(--accent);
    transition: width 1s ease-out;
}
.score-val { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }

/* Link Button */
.p-btn {
    display: inline-block;
    padding: 6px 14px;
    background: transparent;
    color: var(--accent);
    text-decoration: none;
    font-size: 0.8rem; font-weight: 500;
    border-radius: 4px;
    border: 1px solid var(--accent);
    transition: all 0.2s;
    white-space: nowrap;
}
.p-btn:hover { background: var(--accent); color: #000; text-decoration: none; }

/* ── Intent summary strip ── */
.intent {
    display: flex; gap: 32px;
    background: var(--surface);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 28px;
    margin-bottom: 28px;
    z-index: 1; position: relative;
}
.intent-block {}
.intent-lbl { font-size: 0.68rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px; }
.intent-val { font-size: 0.95rem; color: var(--text-primary); font-weight: 500; }

/* ── Section divider ── */
.section-title {
    color: var(--text-primary);
    font-size: 1rem; font-weight: 600;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    margin: 36px 0 22px;
    position: relative; z-index: 1;
}
.section-count { color: var(--text-muted); font-weight: 400; }

/* ── Misc overrides ── */
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
.streamlit-expanderHeader { color: var(--text-secondary) !important; font-size: 0.85rem !important; padding: 16px 24px !important; }

/* Inline Mic Button */
div[data-testid="stAudioInput"] > div { 
    background: var(--surface) !important;
    backdrop-filter: blur(16px);
    border: 1px solid var(--border) !important; 
    border-radius: 16px !important; 
    height: 60px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
}
div[data-testid="stAudioInput"] { width: 100% !important; }

div[data-testid="stExpander"] { 
    background: var(--surface);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border) !important; 
    border-radius: 16px !important; 
    margin-bottom: 24px;
    position: relative; z-index: 1;
}
.stSpinner > div { border-top-color: var(--accent) !important; }

/* hide decoration */
div[data-testid="stDecoration"] { display: none !important; }
</style>
"""

AMBIENT_HTML = """
<div class="ambient">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
</div>
"""

ORB_HTML = """
<div class="orb-wrap">
    <div class="orb-box">
        <div class="orb-halo"></div>
        <div class="rng rng-8"></div>
        <div class="rng rng-7"></div>
        <div class="rng rng-6"></div>
        <div class="rng rng-5"></div>
        <div class="rng rng-4"></div>
        <div class="scan"></div>
        <div class="rng rng-3"></div>
        <div class="rng rng-2"></div>
        <div class="rng rng-1"></div>
        <div class="orb-core">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mic-icon">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
        </div>
        <div class="nd nd-lg nd-1"></div>
        <div class="nd nd-sm nd-2"></div>
        <div class="nd nd-lg nd-3"></div>
        <div class="nd nd-sm nd-4"></div>
        <div class="nd nd-sm nd-5"></div>
        <div class="nd nd-lg nd-6"></div>
    </div>
</div>
"""

JS_CODE = """
<script>
const parentDoc = window.parent.document;
const orbCore = parentDoc.querySelector('.orb-core');

if (orbCore && !orbCore.dataset.listenerAttached) {
    orbCore.dataset.listenerAttached = 'true';
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        
        let isListening = false;
        
        orbCore.addEventListener('click', () => {
            if (!isListening) {
                try {
                    recognition.start();
                } catch(e) {
                    console.error('Speech recognition error:', e);
                }
            } else {
                recognition.stop();
            }
        });
        
        const updateInput = (text) => {
            const inputs = parentDoc.querySelectorAll('input[type="text"]');
            let targetInput = null;
            for(let i=0; i<inputs.length; i++) {
                if (inputs[i].placeholder.includes('What are you looking for')) {
                    targetInput = inputs[i];
                    break;
                }
            }
            
            if(targetInput) {
                let lastValue = targetInput.value;
                targetInput.value = text;
                let event = new Event('input', { bubbles: true });
                let tracker = targetInput._valueTracker;
                if (tracker) {
                    tracker.setValue(lastValue);
                }
                targetInput.dispatchEvent(event);
            }
        };
        
        const triggerSearch = () => {
            const inputs = parentDoc.querySelectorAll('input[type="text"]');
            let targetInput = null;
            for(let i=0; i<inputs.length; i++) {
                if (inputs[i].placeholder.includes('What are you looking for')) {
                    targetInput = inputs[i];
                    break;
                }
            }
            if (targetInput) {
                targetInput.focus();
                let enterEvent = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter', keyCode: 13 });
                targetInput.dispatchEvent(enterEvent);
                targetInput.blur();
            }
            
            setTimeout(() => {
                const buttons = parentDoc.querySelectorAll('button');
                for(let i=0; i<buttons.length; i++) {
                    if (buttons[i].innerText.includes('Analyze & Find Deals')) {
                        buttons[i].click();
                        break;
                    }
                }
            }, 100);
        };
        
        recognition.onstart = () => {
            isListening = true;
            const wrap = parentDoc.querySelector('.orb-wrap');
            if (wrap) wrap.classList.add('listening');
        };
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            const txt = finalTranscript || interimTranscript;
            if (txt) {
                updateInput(txt);
            }
        };
        
        recognition.onend = () => {
            isListening = false;
            const wrap = parentDoc.querySelector('.orb-wrap');
            if (wrap) wrap.classList.remove('listening');
            
            const inputs = parentDoc.querySelectorAll('input[type="text"]');
            let hasText = false;
            for(let i=0; i<inputs.length; i++) {
                if (inputs[i].placeholder.includes('What are you looking for') && inputs[i].value.trim() !== '') {
                    hasText = true;
                    break;
                }
            }
            
            if(hasText) {
                setTimeout(() => {
                    triggerSearch();
                }, 300);
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isListening = false;
            const wrap = parentDoc.querySelector('.orb-wrap');
            if (wrap) wrap.classList.remove('listening');
        };
    } else {
        console.warn('SpeechRecognition not supported in this browser.');
    }
}
</script>
"""

# ═══════════════════════════════════════════════════════════════
#  RENDERING HELPERS
# ═══════════════════════════════════════════════════════════════

def render_product_card(product: dict, rank: int):
    name = product.get("name", "Unknown Product")
    desc = product.get("description", "")
    price = product.get("price", 0)
    rating = product.get("rating")
    review_count = product.get("review_count", 0)
    specs = product.get("specs", [])
    source = product.get("source", "Unknown")
    match_score = product.get("match_score", 0)
    analysis = product.get("review_analysis", {})
    auth_score = analysis.get("authenticity_score", 50)
    url = product.get("url", "#")

    if auth_score >= 85:
        a_cls = "auth-hi"
        verdict_str = f"Verified Genuine &middot; {auth_score}%"
    elif auth_score >= 60:
        a_cls = "auth-ok"
        verdict_str = f"Mostly Authentic &middot; {auth_score}%"
    else:
        a_cls = "auth-lo"
        verdict_str = f"Suspicious &middot; {auth_score}%"

    source_lower = source.lower()
    if "flipkart" in source_lower:
        logo_html = '<img src="https://static-assets-web.flixcart.com/batman-returns/batman-returns/p/images/fkheaderlogo_exploreplus-44005d.svg" class="src-logo" style="height: 16px;"/>'
    elif "amazon" in source_lower:
        logo_html = '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" class="src-logo" style="height: 12px; filter: brightness(0) invert(1);"/>'
    else:
        logo_html = source

    chips = "".join(f'<span class="chip">{s}</span>' for s in specs[:5])
    chips_html = f'<div class="specs">{chips}</div>' if chips else ""

    rating_html = ""
    if rating:
        try:
            r_val = float(rating)
            stars_str = "★" * round(r_val) + "☆" * (5 - round(r_val))
        except:
            stars_str = "★" * 4 + "☆"

        rating_html = f'<div class="p-rating"><span class="stars">{stars_str}</span> <strong>{rating}</strong>'
        if review_count:
            rating_html += f' &middot; {review_count:,} reviews'
        rating_html += '</div>'

    desc_html = f'<div class="p-desc">{desc}</div>' if desc else ""

    thumbnail = product.get("thumbnail", "")
    thumb_html = f'<div class="p-img-wrap"><img src="{thumbnail}" alt="product image"/></div>' if thumbnail else '<div class="p-img-wrap"><span style="color:#888; font-size:0.8rem">No Image</span></div>'

    st.markdown(f"""
<div class="p-card" style="animation-delay: {rank * 0.1}s;">
<div class="p-rank">#{rank}</div>
{thumb_html}
<div class="p-content">
<div class="p-header-row">
<div class="p-name"><a href="{url}" target="_blank">{name}</a></div>
</div>
{desc_html}
<div class="p-price-row">
<span class="p-price">₹{price:,.0f}</span>
<span class="p-source">{logo_html}</span>
</div>

<div class="p-meta-row">
{rating_html}
<span class="auth {a_cls}">{verdict_str}</span>
</div>

{chips_html}

<div class="p-bottom-row">
<div class="score-wrap">
<span class="score-lbl">Value Match</span>
<div class="bar-bg"><div class="bar-fill" style="width:{match_score}%"></div></div>
<span class="score-val">{match_score:.1f}</span>
</div>
<a href="{url}" target="_blank" class="p-btn">View Deal &rarr;</a>
</div>
</div>
</div>
""", unsafe_allow_html=True)


def render_intent(parsed: dict):
    pt = parsed.get("product_type", "N/A").title()
    budget = parsed.get("budget")
    bd = f"₹{budget:,}" if budget else "No limit"
    sq = parsed.get("search_query", "—")
    st.markdown(f"""
<div class="intent">
<div class="intent-block"><div class="intent-lbl">Category</div><div class="intent-val">{pt}</div></div>
<div class="intent-block"><div class="intent-lbl">Budget</div><div class="intent-val">{bd}</div></div>
<div class="intent-block"><div class="intent-lbl">Query</div><div class="intent-val">{sq}</div></div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(AMBIENT_HTML, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
<div class="hero">
<div class="hero-label">AI-Powered</div>
<div class="hero-title">Shopping Intelligence</div>
<div class="hero-sub">Find the best deals across Flipkart and Amazon — ranked by real value, with AI-verified reviews.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(ORB_HTML, unsafe_allow_html=True)
    components.html(JS_CODE, height=0, width=0)

    # ── Search & Voice Inline ──
    text_query = st.text_input(
        "Search",
        placeholder="What are you looking for? e.g. Wireless headphones under 3000",
        key="q",
        label_visibility="collapsed"
    )

    final_query = text_query

    # ── Action ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        go = st.button("Analyze & Find Deals", use_container_width=True)

    # ── Pipeline ──
    if go and final_query:
        st.markdown("<br>", unsafe_allow_html=True)

        with st.spinner("Parsing intent..."):
            from agent import parse_query
            parsed = parse_query(final_query)
        render_intent(parsed)

        with st.spinner("Scanning products across stores..."):
            from scraper import scrape_products, get_demo_products
            products = scrape_products(parsed["search_query"], max_per_source=8)
            if not products:
                products = get_demo_products(parsed["product_type"])

        if parsed.get("budget") and products:
            budget = parsed["budget"]
            filtered = [p for p in products if p.get("price") and p["price"] <= budget * 1.2]
            if filtered:
                products = filtered

        with st.spinner("Analyzing review authenticity..."):
            from review_analyzer import analyze_reviews
            products = analyze_reviews(products)

        with st.spinner("Ranking by value..."):
            from agent import rank_products, filter_top_5_with_groq
            products = rank_products(products, parsed.get("budget"))
            
        with st.spinner("Filtering top 5 using Groq AI..."):
            products = filter_top_5_with_groq(products, final_query)

        st.markdown(f'<div class="section-title">Results <span class="section-count">({len(products)})</span></div>', unsafe_allow_html=True)

        for i, product in enumerate(products):
            render_product_card(product, rank=i + 1)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        def reset_search():
            st.session_state.q = ""
            
        rc1, rc2, rc3 = st.columns([1, 2, 1])
        with rc2:
            st.button("Search New Product", on_click=reset_search, use_container_width=True)

    elif go and not final_query:
        st.warning("Enter a search query or use voice input first.")


if __name__ == "__main__":
    main()
