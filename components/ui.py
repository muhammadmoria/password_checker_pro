"""Reusable UI components with glassmorphism styling."""
import streamlit as st
from pathlib import Path
from config import settings


def load_css():
    """Load and inject the custom CSS stylesheet."""
    css_path = settings.assets_dir / "style.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_background():
    """Render the animated particle background."""
    st.components.v1.html(
        """
        <canvas id="bg-canvas" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;"></canvas>
        <script>
        (function(){
            const canvas = document.getElementById('bg-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            let w, h, particles;

            function resize(){
                w = canvas.width = window.innerWidth;
                h = canvas.height = window.innerHeight;
            }

            function initParticles(){
                const count = Math.min(80, Math.floor(w * h / 18000));
                particles = [];
                for (let i = 0; i < count; i++){
                    particles.push({
                        x: Math.random() * w,
                        y: Math.random() * h,
                        vx: (Math.random() - 0.5) * 0.3,
                        vy: (Math.random() - 0.5) * 0.3,
                        r: Math.random() * 2 + 0.5,
                        c: Math.random() > 0.5 ? '0, 212, 255' : '189, 0, 255',
                        a: Math.random() * 0.5 + 0.1
                    });
                }
            }

            function draw(){
                ctx.clearRect(0, 0, w, h);
                for (let i = 0; i < particles.length; i++){
                    const p = particles[i];
                    p.x += p.vx;
                    p.y += p.vy;
                    if (p.x < 0) p.x = w;
                    if (p.x > w) p.x = 0;
                    if (p.y < 0) p.y = h;
                    if (p.y > h) p.y = 0;

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(' + p.c + ', ' + p.a + ')';
                    ctx.fill();

                    for (let j = i + 1; j < particles.length; j++){
                        const q = particles[j];
                        const dx = p.x - q.x;
                        const dy = p.y - q.y;
                        const dist = Math.sqrt(dx*dx + dy*dy);
                        if (dist < 120){
                            ctx.beginPath();
                            ctx.moveTo(p.x, p.y);
                            ctx.lineTo(q.x, q.y);
                            ctx.strokeStyle = 'rgba(' + p.c + ', ' + (0.15 * (1 - dist/120)) + ')';
                            ctx.lineWidth = 0.5;
                            ctx.stroke();
                        }
                    }
                }
                requestAnimationFrame(draw);
            }

            resize();
            initParticles();
            draw();
            window.addEventListener('resize', function(){ resize(); initParticles(); });
        })();
        </script>
        """,
        height=0,
    )


def glass_card(content: str, height: str | None = None):
    """Render a glassmorphism card with HTML content."""
    style = f'style="min-height:{height};"' if height else ""
    st.markdown(
        f'<div class="glass-card" {style}>{content}</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str = "", color: str = "#00d4ff"):
    """Render a metric card with neon styling."""
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 3px solid {color};">
            <div class="metric-icon" style="color:{color};">{icon}</div>
            <div class="metric-content">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def neon_button_label(text: str, color: str = "#00d4ff") -> str:
    """Return styled button label HTML."""
    return f'<span style="color:{color};font-weight:600;">{text}</span>'


def info_banner(message: str, type_: str = "info"):
    """Render a styled info/warning/error banner."""
    colors = {
        "info": ("#00d4ff", "#0a1929"),
        "warning": ("#f59e0b", "#1a1500"),
        "error": ("#ef4444", "#1a0a0a"),
        "success": ("#10b981", "#0a1a12"),
    }
    color, bg = colors.get(type_, colors["info"])
    st.markdown(
        f"""
        <div class="info-banner" style="border-color:{color};background:{bg};">
            <span style="color:{color};">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = ""):
    """Render a section header with icon."""
    st.markdown(
        f'<div class="section-header"><span class="section-icon">{icon}</span><span class="section-title">{title}</span></div>',
        unsafe_allow_html=True,
    )