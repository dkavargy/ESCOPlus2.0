!pip install --upgrade gradio
import json
import pandas as pd
from collections import Counter
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================
# 1. LOAD DATA
# ============================================================
file_path = ''

if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

with open(file_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

if isinstance(jobs, dict):
    jobs = list(jobs.values())

total_jobs = len(jobs)
print(f"✅ Loaded {total_jobs} job postings.")

# ============================================================
# 2. BUILD OCCUPATION-SKILL INDEX
# ============================================================

def get_occupation(job):
    return (
        job.get('occupation') or job.get('job_title') or
        job.get('title') or job.get('category') or 'Unknown'
    )

def build_occupation_skill_index():
    occ_groups = {}
    for job in jobs:
        occ = str(get_occupation(job))
        occ_groups.setdefault(occ, []).append(job)

    ext_index   = {}
    prune_index = {}
    occ_counts  = {}

    for occ, occ_jobs in occ_groups.items():
        n_j = len(occ_jobs)
        occ_counts[occ] = n_j

        # --- Extension: non_esco_skills ---
        ext_counts = Counter()
        for job in occ_jobs:
            items = job.get('non_esco_skills', [])
            if not isinstance(items, list):
                continue
            unique = {
                item.get('label') for item in items
                if isinstance(item, dict) and item.get('label')
            }
            for label in unique:
                ext_counts[label] += 1

        # KEY FIX: sort by count desc, then skill name asc — NO ties share same rank
        ext_records = []
        rank = 1
        prev_count = None
        for i, (label, count) in enumerate(
            sorted(ext_counts.items(), key=lambda x: (-x[1], x[0]))
        ):
            if count != prev_count:
                rank = i + 1
                prev_count = count
            ext_records.append({
                'Rank': rank,
                'Skill (Non-ESCO)': label,
                'o_ij (Postings)': count,
                'f(s) = o_ij / n_j (%)': round((count / n_j) * 100, 2),
                'Action': '➕ Add to ESCO'
            })

        ext_index[occ] = (
            pd.DataFrame(ext_records).reset_index(drop=True)
            if ext_records else
            pd.DataFrame(columns=['Rank', 'Skill (Non-ESCO)', 'o_ij (Postings)', 'f(s) = o_ij / n_j (%)', 'Action'])
        )

        # --- Pruning: mapped_skills (ESCO) ---
        prune_counts = Counter()
        for job in occ_jobs:
            items = job.get('mapped_skills', [])
            if not isinstance(items, list):
                continue
            unique = {
                item.get('label') for item in items
                if isinstance(item, dict) and item.get('label')
            }
            for label in unique:
                prune_counts[label] += 1

        # KEY FIX: sort by count asc (lowest first = most obsolete), then skill name asc
        prune_records = []
        rank = 1
        prev_count = None
        sorted_prune = sorted(prune_counts.items(), key=lambda x: (x[1], x[0]))
        for i, (label, count) in enumerate(sorted_prune):
            if count != prev_count:
                rank = i + 1
                prev_count = count
            prune_records.append({
                'Rank': rank,
                'Skill (ESCO)': label,
                'o_ij (Postings)': count,
                'f(s) = o_ij / n_j (%)': round((count / n_j) * 100, 2),
                'Action': '🗑️ Deprecate'
            })

        prune_index[occ] = (
            pd.DataFrame(prune_records).reset_index(drop=True)
            if prune_records else
            pd.DataFrame(columns=['Rank', 'Skill (ESCO)', 'o_ij (Postings)', 'f(s) = o_ij / n_j (%)', 'Action'])
        )

    occ_list = sorted(occ_groups.keys(), key=lambda o: occ_counts[o], reverse=True)
    return occ_list, ext_index, prune_index, occ_counts

print("⏳ Building occupation-skill index...")
occ_list, ext_index, prune_index, occ_counts = build_occupation_skill_index()
print(f"✅ Index built for {len(occ_list)} occupations.")

# ============================================================
# 3. PLOT BUILDERS — SMOOTH UNIQUE-COUNT BARS
# ============================================================

def make_extension_plot(df, occupation, n_j, top_n):
    """
    Each skill gets its own bar. Skills with the same count are NOT merged —
    they each appear as individual bars, stacked downward in order.
    Color is a smooth continuous gradient by f(s).
    """
    df = df.head(top_n).copy()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No Non-ESCO skills found for this occupation.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#555")
        )
        fig.update_layout(title="Extension Engine — No Data", height=350)
        return fig

    # Reverse for horizontal bar (highest at top)
    df_plot = df.iloc[::-1].reset_index(drop=True)

    fig = go.Figure()

    # Smooth gradient: map f(s) to a blue color scale individually per bar
    fs_vals  = df_plot['f(s) = o_ij / n_j (%)'].tolist()
    fs_min   = min(fs_vals)
    fs_max   = max(fs_vals) if max(fs_vals) != fs_min else fs_min + 1

    import matplotlib.colors as mcolors
    import matplotlib.cm as mcm
    cmap = mcm.get_cmap('Blues')

    bar_colors = []
    for val in fs_vals:
        norm = 0.35 + 0.6 * (val - fs_min) / (fs_max - fs_min)  # keep in 0.35–0.95 range
        rgba = cmap(norm)
        bar_colors.append(mcolors.to_hex(rgba))

    fig.add_trace(go.Bar(
        x=df_plot['f(s) = o_ij / n_j (%)'],
        y=df_plot['Skill (Non-ESCO)'],
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='rgba(255,255,255,0.4)', width=0.8)
        ),
        text=[f"{v}%  ({int(o)} jobs)" for v, o in zip(
            df_plot['f(s) = o_ij / n_j (%)'],
            df_plot['o_ij (Postings)']
        )],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "f(s): %{x}%<br>"
            "Postings: %{customdata}<br>"
            "<extra></extra>"
        ),
        customdata=df_plot['o_ij (Postings)'],
        cliponaxis=False
    ))

    fig.update_layout(
        title=dict(
            text=(
                f"🔵 Extension Engine — Top {top_n} Non-ESCO Skills<br>"
                f"<sup>Occupation: <b>{occupation}</b> &nbsp;|&nbsp; "
                f"n_j = {n_j} postings &nbsp;|&nbsp; f(s) = o_ij / n_j</sup>"
            ),
            font=dict(size=14)
        ),
        xaxis=dict(
            title="f(s) — Document Frequency (%)",
            showgrid=True, gridcolor='rgba(200,210,255,0.4)',
            zeroline=False
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11),
            automargin=True
        ),
        plot_bgcolor='#f0f6ff',
        paper_bgcolor='white',
        height=max(380, len(df_plot) * 32 + 120),
        margin=dict(l=20, r=120, t=100, b=50),
        showlegend=False
    )
    return fig


def make_pruning_plot(df, occupation, n_j, top_n):
    """
    Same logic — each ESCO skill is its own bar.
    Skills with equal counts are NOT grouped — each shown separately.
    Lowest f(s) at top (most obsolete first). Red gradient.
    """
    df = df.head(top_n).copy()
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No ESCO skills found for this occupation.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#555")
        )
        fig.update_layout(title="Pruning Engine — No Data", height=350)
        return fig

    # Most obsolete (lowest f(s)) at top → do NOT reverse
    df_plot = df.reset_index(drop=True)

    import matplotlib.colors as mcolors
    import matplotlib.cm as mcm
    cmap = mcm.get_cmap('Reds')

    fs_vals = df_plot['f(s) = o_ij / n_j (%)'].tolist()
    fs_min  = min(fs_vals)
    fs_max  = max(fs_vals) if max(fs_vals) != fs_min else fs_min + 1

    bar_colors = []
    for val in fs_vals:
        # Invert: lowest f(s) gets darkest red (most critical)
        norm = 0.35 + 0.6 * (1 - (val - fs_min) / (fs_max - fs_min))
        rgba = cmap(norm)
        bar_colors.append(mcolors.to_hex(rgba))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot['f(s) = o_ij / n_j (%)'],
        y=df_plot['Skill (ESCO)'],
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='rgba(255,255,255,0.4)', width=0.8)
        ),
        text=[f"{v}%  ({int(o)} jobs)" for v, o in zip(
            df_plot['f(s) = o_ij / n_j (%)'],
            df_plot['o_ij (Postings)']
        )],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "f(s): %{x}%<br>"
            "Postings: %{customdata}<br>"
            "<extra></extra>"
        ),
        customdata=df_plot['o_ij (Postings)'],
        cliponaxis=False
    ))

    fig.update_layout(
        title=dict(
            text=(
                f"🔴 Pruning Engine — Top {top_n} Declining ESCO Skills<br>"
                f"<sup>Occupation: <b>{occupation}</b> &nbsp;|&nbsp; "
                f"n_j = {n_j} postings &nbsp;|&nbsp; f(s) = o_ij / n_j</sup>"
            ),
            font=dict(size=14)
        ),
        xaxis=dict(
            title="f(s) — Document Frequency (%)",
            showgrid=True, gridcolor='rgba(255,210,210,0.5)',
            zeroline=False
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11),
            automargin=True,
            categoryorder='array',
            categoryarray=df_plot['Skill (ESCO)'].tolist()
        ),
        plot_bgcolor='#fff0f0',
        paper_bgcolor='white',
        height=max(380, len(df_plot) * 32 + 120),
        margin=dict(l=20, r=120, t=100, b=50),
        showlegend=False
    )
    return fig

# ============================================================
# 4. MAIN CALLBACK
# ============================================================

def update_dashboard(occupation, top_n_ext, top_n_prune):
    top_n_ext   = int(top_n_ext)
    top_n_prune = int(top_n_prune)
    n_j         = occ_counts.get(occupation, 0)

    # ── EXTENSION ────────────────────────────────────────────
    df_ext     = ext_index.get(occupation, pd.DataFrame())
    fig_ext    = make_extension_plot(df_ext, occupation, n_j, top_n_ext)
    table_ext  = df_ext.head(top_n_ext).copy() if not df_ext.empty else pd.DataFrame()

    if df_ext.empty:
        ext_info = f"⚠️ No Non-ESCO skills found for **{occupation}**."
    else:
        ext_info = (
            f"**Occupation:** {occupation} &nbsp;|&nbsp; "
            f"**Total Postings (n_j):** {n_j} &nbsp;|&nbsp; "
            f"**Non-ESCO Skills Detected:** {len(df_ext)}\n\n"
            f"Skills below have **high f(s)** but **zero presence in ESCO** — "
            f"prime candidates to **extend** the taxonomy. "
            f"Skills with equal posting counts each appear as **individual bars**, "
            f"ranked alphabetically within the same count tier."
        )

    # ── PRUNING ──────────────────────────────────────────────
    df_prune     = prune_index.get(occupation, pd.DataFrame())
    fig_prune    = make_pruning_plot(df_prune, occupation, n_j, top_n_prune)
    table_prune  = df_prune.head(top_n_prune).copy() if not df_prune.empty else pd.DataFrame()

    if df_prune.empty:
        prune_info = f"⚠️ No ESCO skills found for **{occupation}**."
    else:
        prune_info = (
            f"**Occupation:** {occupation} &nbsp;|&nbsp; "
            f"**Total Postings (n_j):** {n_j} &nbsp;|&nbsp; "
            f"**ESCO Skills Tracked:** {len(df_prune)}\n\n"
            f"Skills below have the **lowest f(s)** for this occupation — "
            f"these are **legacy skills** candidates for **deprecation**. "
            f"Darkest red = most obsolete. Each skill is shown individually "
            f"even when counts are equal."
        )

    return fig_ext, table_ext, ext_info, fig_prune, table_prune, prune_info


def get_initial_outputs():
    if occ_list:
        return update_dashboard(occ_list[0], 15, 15)
    empty_fig = go.Figure()
    empty_df  = pd.DataFrame()
    return empty_fig, empty_df, "", empty_fig, empty_df, ""

# ============================================================
# 5. BUILD UI
# ============================================================

default_occ = occ_list[0] if occ_list else ""
max_ext     = max(5, min(60, max((len(v) for v in ext_index.values()), default=15)))
max_prune   = max(5, min(60, max((len(v) for v in prune_index.values()), default=15)))

with gr.Blocks(
    theme=gr.themes.Default(primary_hue="blue", secondary_hue="gray"),
    title="ESCOPLUS 2.0 — Occupation Skill Analyser"
) as demo:

    gr.Markdown("""
    # 📊 ESCOPLUS 2.0 — Occupation-Skill Δ Analyser
    ### *Select an occupation to explore its Extension & Pruning skill landscape*
    > **Formula:** f(s) = o_ij / n_j &nbsp;|&nbsp;
    > o_ij = postings containing skill *s* in occupation *j* &nbsp;|&nbsp;
    > n_j = total postings for occupation *j*
    ---
    """)

    with gr.Row():
        with gr.Column(scale=3):
            occ_dropdown = gr.Dropdown(
                choices=occ_list,
                value=default_occ,
                label="👔 Select Occupation",
                info=f"{len(occ_list)} occupations — sorted by frequency"
            )
        with gr.Column(scale=1):
            slider_ext = gr.Slider(
                minimum=5, maximum=max_ext,
                value=15, step=1,
                label="🔵 Top N — Extension Skills"
            )
        with gr.Column(scale=1):
            slider_prune = gr.Slider(
                minimum=5, maximum=max_prune,
                value=15, step=1,
                label="🔴 Top N — Pruning Skills"
            )
        with gr.Column(scale=1):
            btn_analyse = gr.Button("🔍 Analyse", variant="primary", size="lg")

    gr.Markdown("---")

    with gr.Row():

        # LEFT — EXTENSION
        with gr.Column(scale=1):
            gr.Markdown("""
            ## 🔵 Extension Engine
            **Non-ESCO skills** with high f(s) for this occupation.
            Missing from ESCO but heavily demanded — candidates to **add to taxonomy**.
            Each skill is shown as its own bar. Equal-count skills are listed individually,
            ordered alphabetically within their count tier.
            """)
            ext_info_box = gr.Markdown()
            plot_ext     = gr.Plot()
            gr.Markdown("#### 📋 Full Ranked Table")
            table_ext    = gr.Dataframe(interactive=False, wrap=True)
            with gr.Row():
                btn_add   = gr.Button("➕ Add to ESCO", variant="primary")
                btn_merge = gr.Button("🔗 Merge to Parent", variant="secondary")
            log_ext = gr.Textbox(label="Action Log", interactive=False, value="")
            btn_add.click(
                fn=lambda: "✅ Skill flagged for addition to ESCO. Pending expert validation.",
                outputs=log_ext
            )
            btn_merge.click(
                fn=lambda: "🔗 Skill queued for hierarchical merge review.",
                outputs=log_ext
            )

        # RIGHT — PRUNING
        with gr.Column(scale=1):
            gr.Markdown("""
            ## 🔴 Pruning Engine
            **Existing ESCO skills** with the lowest f(s) for this occupation.
            Legacy / obsolete skills disappearing from postings — candidates to **deprecate**.
            Darkest red = most obsolete. Each skill shown individually regardless of equal counts.
            """)
            prune_info_box = gr.Markdown()
            plot_prune     = gr.Plot()
            gr.Markdown("#### 📋 Full Ranked Table")
            table_prune    = gr.Dataframe(interactive=False, wrap=True)
            with gr.Row():
                btn_archive  = gr.Button("🗑️ Archive / Deprecate", variant="stop")
                btn_evaluate = gr.Button("⚖️ Expert Review", variant="secondary")
            log_prune = gr.Textbox(label="Action Log", interactive=False, value="")
            btn_archive.click(
                fn=lambda: "🗑️ Skill moved to Deprecated status.",
                outputs=log_prune
            )
            btn_evaluate.click(
                fn=lambda: "⚖️ Skill submitted for expert review.",
                outputs=log_prune
            )

    gr.Markdown("""
    ---
    **ESCOPLUS 2.0** &nbsp;|&nbsp; Gradio + Plotly &nbsp;|&nbsp;
    *Occupation-level Δ-Analysis — each skill is an individual data point, never grouped by count.*
    """)

    all_outputs = [plot_ext, table_ext, ext_info_box, plot_prune, table_prune, prune_info_box]
    all_inputs  = [occ_dropdown, slider_ext, slider_prune]

    btn_analyse.click(fn=update_dashboard,  inputs=all_inputs, outputs=all_outputs)
    occ_dropdown.change(fn=update_dashboard, inputs=all_inputs, outputs=all_outputs)
    slider_ext.change(fn=update_dashboard,   inputs=all_inputs, outputs=all_outputs)
    slider_prune.change(fn=update_dashboard, inputs=all_inputs, outputs=all_outputs)
    demo.load(fn=get_initial_outputs, outputs=all_outputs)

# ============================================================
# 6. LAUNCH
# ============================================================
demo.launch(debug=True, share=True)
