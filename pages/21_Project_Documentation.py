"""
QuantTerminal — Project Documentation Viewer.

Displays the 30-page QuantTerminal_Project_Documentation.pdf inside the app with
page navigation, chapter jump, a high-resolution page renderer, an embedded PDF
viewer mode, a quick-jump table of contents and a download button.
"""

import base64
import os
import sys

import streamlit as st

# Ensure root directory is in path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from utils.helper import inject_custom_theme, render_disclaimer_footer
from utils.sidebar import render_sidebar

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF releases
    try:
        import fitz
    except ImportError:
        fitz = None

# =============================================================================
# 1. Page Configuration & Theme (MUST BE FIRST STREAMLIT CALL)
# =============================================================================
st.set_page_config(
    page_title="Project Documentation — QuantTerminal",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_theme()
render_sidebar()

PDF_NAME = "QuantTerminal_Project_Documentation.pdf"
PDF_PATH = os.path.join(_root_dir, PDF_NAME)

# (title, description, start page)
CHAPTERS = [
    ("Cover & Table of Contents", "Title page, version details and the full contents list", 1),
    ("Disclaimer & How to Read", "Educational-use notice and what Bullish, Bearish and Neutral mean", 3),
    ("1. About This Project", "What QuantTerminal is, who it is for and its core promises", 4),
    ("2. Key Features", "Seven research domains and the five featured workspaces", 5),
    ("3. Terminal Use Cases", "Six practical ways to use the terminal, with examples", 6),
    ("4. Roles & Credits", "Team, workstreams and the 30-day plan", 8),
    ("5. Installation", "Requirements and step-by-step setup", 9),
    ("6. Tour of the Screen", "Annotated home page and sidebar controls", 10),
    ("7. How to Use the Terminal", "Six steps from picking a stock to exporting results", 11),
    ("8. Recommended Workflows", "Suggested module routes for common goals", 12),
    ("9. System Architecture", "Layers, folders and request flow", 13),
    ("10. The Data Layer", "Data sources, preparation and supported settings", 14),
    ("11. Method & Bias Controls", "How look-ahead and leakage are avoided; core formulas", 15),
    ("Module Reference (20 modules)", "Dashboard through Credits, two modules per page", 16),
    ("Quick-Reference Table", "One-line summary of every module", 26),
    ("12. Glossary", "Simple meanings of 27 terms", 27),
    ("13. Capability Matrix & Stack", "What each module covers, plus technologies", 28),
    ("14. Testing & Roadmap", "Tests, honest limitations and future work", 29),
    ("15. FAQ & Appendix", "Troubleshooting and the docs folder map", 30),
]


@st.cache_data(show_spinner=False)
def _load_pdf_bytes(path: str, mtime: float):
    with open(path, "rb") as fh:
        return fh.read()


@st.cache_data(show_spinner=False)
def _page_count(path: str, mtime: float) -> int:
    if fitz is None:
        return 30
    with fitz.open(path) as doc:
        return len(doc)


@st.cache_data(show_spinner=False)
def _render_page(path: str, mtime: float, page_no: int, dpi: int) -> bytes:
    with fitz.open(path) as doc:
        pix = doc[page_no - 1].get_pixmap(dpi=dpi)
        return pix.tobytes("png")


@st.cache_data(show_spinner=False)
def _page_text(path: str, mtime: float, page_no: int) -> str:
    if fitz is None:
        return ""
    with fitz.open(path) as doc:
        return doc[page_no - 1].get_text()


# =============================================================================
# 2. Load document
# =============================================================================
if not os.path.isfile(PDF_PATH):
    st.error(f"Documentation file `{PDF_NAME}` was not found in the project root.")
    render_disclaimer_footer()
    st.stop()

mtime = os.path.getmtime(PDF_PATH)
pdf_bytes = _load_pdf_bytes(PDF_PATH, mtime)
total_pages = _page_count(PDF_PATH, mtime)
size_mb = len(pdf_bytes) / (1024 * 1024)


def _chapter_label(idx: int) -> str:
    title, _, pg = CHAPTERS[idx]
    return f"Page {pg:02d}: {title}"


def _chapter_for_page(pg: int) -> int:
    idx = 0
    for i, (_, _, start) in enumerate(CHAPTERS):
        if start <= pg:
            idx = i
    return idx


if "doc_page" not in st.session_state:
    st.session_state["doc_page"] = 1
if "doc_page_num" not in st.session_state:
    st.session_state["doc_page_num"] = 1
if "doc_jump" not in st.session_state:
    st.session_state["doc_jump"] = _chapter_label(0)


def _goto(pg: int):
    """Move to a page and keep every navigation widget in sync."""
    pg = max(1, min(total_pages, int(pg)))
    st.session_state["doc_page"] = pg
    st.session_state["doc_page_num"] = pg
    st.session_state["doc_jump"] = _chapter_label(_chapter_for_page(pg))


def _on_jump():
    label = st.session_state["doc_jump"]
    for i in range(len(CHAPTERS)):
        if _chapter_label(i) == label:
            _goto(CHAPTERS[i][2])
            return


def _on_num():
    _goto(st.session_state["doc_page_num"])


# =============================================================================
# 3. Styling
# =============================================================================
st.markdown(
    """
    <style>
    .qt-doc-hero {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1px solid rgba(255, 255, 255, 0.10); border-radius: 16px;
        padding: 26px 30px; margin-bottom: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
    }
    .qt-doc-badge {
        display: inline-block; background: rgba(56, 189, 248, 0.12); color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 4px 12px;
        font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; margin-bottom: 10px;
    }
    .qt-doc-title { font-size: 2rem; font-weight: 800; color: #F8FAFC; margin: 0 0 6px 0; }
    .qt-doc-sub { font-size: 0.9rem; color: #94A3B8; max-width: 760px; line-height: 1.5; }
    .qt-doc-status {
        background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.10);
        border-radius: 12px; padding: 14px 20px; text-align: center; min-width: 190px;
    }
    .qt-doc-status .a { color: #10B981; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; }
    .qt-doc-status .b { color: #F8FAFC; font-size: 1.15rem; font-weight: 800; margin: 4px 0 2px 0; }
    .qt-doc-status .c { color: #94A3B8; font-size: 0.72rem; }
    .qt-doc-card {
        background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 12px 14px; min-height: 84px; margin-bottom: 6px;
    }
    .qt-doc-card .t { display: flex; justify-content: space-between; gap: 8px; color: #F8FAFC; font-weight: 700; font-size: 0.88rem; }
    .qt-doc-card .p {
        background: rgba(37, 99, 235, 0.25); color: #BFDBFE; border-radius: 6px;
        padding: 1px 8px; font-size: 0.7rem; white-space: nowrap; height: fit-content;
    }
    .qt-doc-card .d { color: #94A3B8; font-size: 0.78rem; margin-top: 6px; line-height: 1.4; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# 4. Hero
# =============================================================================
st.markdown(
    f"""
    <div class="qt-doc-hero">
        <div>
            <div class="qt-doc-badge">PROJECT DOCUMENTATION</div>
            <div class="qt-doc-title">📘 QuantTerminal Project Documentation</div>
            <div class="qt-doc-sub">
                A complete, plain-language guide: about the project, credits, use cases, how to use the
                terminal and a detailed explanation of every module.
            </div>
        </div>
        <div class="qt-doc-status">
            <div class="a">● DOCUMENT READY</div>
            <div class="b">{total_pages} Pages Complete</div>
            <div class="c">{size_mb:.1f} MB PDF Document</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# 5. Controls
# =============================================================================
c_jump, c_nav, c_exp = st.columns([4.2, 3.6, 3.0])

with c_jump:
    st.markdown("**📍 Jump to Section / Chapter:**")
    st.selectbox(
        "Jump to Section / Chapter",
        [_chapter_label(i) for i in range(len(CHAPTERS))],
        key="doc_jump",
        on_change=_on_jump,
        label_visibility="collapsed",
    )

with c_nav:
    st.markdown("**📖 Page Navigation:**")
    n1, n2, n3 = st.columns([1, 1.4, 1])
    n1.button("◀ Prev", key="doc_prev", width="stretch",
              on_click=lambda: _goto(st.session_state["doc_page"] - 1))
    n2.number_input("Page", min_value=1, max_value=total_pages, step=1, key="doc_page_num",
                    on_change=_on_num, label_visibility="collapsed")
    n3.button("Next ▶", key="doc_next", width="stretch",
              on_click=lambda: _goto(st.session_state["doc_page"] + 1))
    f1, f2 = st.columns(2)
    f1.button("⏮ First Page (Cover)", key="doc_first", width="stretch", on_click=lambda: _goto(1))
    f2.button(f"⏭ Last Page ({total_pages})", key="doc_last", width="stretch",
              on_click=lambda: _goto(total_pages))

with c_exp:
    st.markdown("**📥 Export & Mode:**")
    st.download_button(
        f"📥 Download PDF ({size_mb:.1f} MB)",
        data=pdf_bytes,
        file_name=PDF_NAME,
        mime="application/pdf",
        key="doc_download",
        width="stretch",
    )
    mode_options = ["High-Res Page Render", "Embedded PDF Viewer"] if fitz is not None else ["Embedded PDF Viewer"]
    mode = st.radio("Reader Mode:", mode_options, horizontal=True, key="doc_mode")

# =============================================================================
# 6. Reader
# =============================================================================
page_no = st.session_state["doc_page"]
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

if mode == "High-Res Page Render":
    h_l, h_r = st.columns([6, 4])
    with h_l:
        st.markdown(f"### 📄 Page {page_no} of {total_pages}")
    with h_r:
        dpi = st.slider("Render Quality (DPI)", 80, 220, 140, step=10, key="doc_dpi")

    with st.spinner("Rendering page…"):
        img = _render_page(PDF_PATH, mtime, page_no, dpi)
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        st.image(img, caption=f"QuantTerminal Project Documentation — Page {page_no}/{total_pages}",
                 width="stretch")

    b1, b2, b3 = st.columns([3, 4, 3])
    b1.button("⬅️ Previous Page", key="doc_prev_b", width="stretch",
              disabled=page_no <= 1, on_click=lambda: _goto(page_no - 1))
    b2.markdown(
        f"<div style='text-align:center; padding-top:8px; font-weight:600; color:#E2E8F0;'>Displaying Page {page_no} of {total_pages}</div>",
        unsafe_allow_html=True,
    )
    b3.button("Next Page ➡️", key="doc_next_b", width="stretch",
              disabled=page_no >= total_pages, on_click=lambda: _goto(page_no + 1))

    with st.expander(f"📝 Extracted Text & Data (Page {page_no})"):
        st.text(_page_text(PDF_PATH, mtime, page_no) or "No text could be extracted for this page.")
else:
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    st.markdown(f"### 📄 Embedded PDF Viewer (opens at page {page_no})")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}#page={page_no}" width="100%" height="900" '
        f'style="border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;"></iframe>',
        unsafe_allow_html=True,
    )
    st.caption("If the viewer is blank, your browser may block embedded PDFs. Use Download PDF or the High-Res Page Render mode.")

# =============================================================================
# 7. Table of contents & quick jump
# =============================================================================
st.markdown("---")
st.markdown("### 📑 Full Table of Contents & Quick Jump Directory")
st.caption("Click any chapter card below to open that section of the documentation.")

for row_start in range(0, len(CHAPTERS), 3):
    cols = st.columns(3)
    for col, idx in zip(cols, range(row_start, min(row_start + 3, len(CHAPTERS)))):
        title, desc, pg = CHAPTERS[idx]
        with col:
            st.markdown(
                f"""
                <div class="qt-doc-card">
                    <div class="t"><span>{title}</span><span class="p">Page {pg}</span></div>
                    <div class="d">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(f"Go to Page {pg}", key=f"doc_toc_{idx}", width="stretch",
                      on_click=_goto, args=(pg,))

render_disclaimer_footer()
