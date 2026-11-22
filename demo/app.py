"""Interactive panel demo for DriftCapsNet.

Run with:
    .venv\\Scripts\\streamlit.exe run demo\\app.py

Loads the trained Stage-A checkpoint (data/stage3_model/model_state.pt, not shipped: see README §6) and lets a user
type a post (English / Hindi / Hinglish) and see the live tier prediction, per-tier
probabilities, and a live 32-step Integrated Gradients word-level explanation, cross-checked
against the project's own clinical lexicon -- no retraining happens here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import datetime
import json
import streamlit as st

from inference import get_pipeline, TIER_NAMES, TIER_COLORS

st.set_page_config(page_title="Hinglish Mental-Health Risk Screening — Live Demo", page_icon="🩺", layout="centered")

st.markdown(
    """
    <div style="background:#fff3cd;border:1px solid #ffe58f;border-radius:8px;padding:12px 16px;margin-bottom:18px;">
    <strong>⚕️ Screening aid, not a diagnostic tool.</strong> This system produces tier-level risk
    <em>signals</em> to help prioritise human attention. Its outputs are <strong>not</strong> clinical
    diagnoses and carry no clinical authority. Every flagged case requires review by a qualified human
    before any action is taken.
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("🩺 Cross-Platform Hinglish Mental-Health Risk Screening")
st.caption(
    "DriftCapsNet — dual frozen backbones (MuRIL + xlm-emo-t), capsule routing, cross-modal attention "
    "fusion, focal + supervised-contrastive loss. Trained on YouTube, evaluated on unseen Reddit + Twitter/X."
)


@st.cache_resource(show_spinner="Loading MuRIL, the emotion backbone, and the trained model (first run only)...")
def _load():
    return get_pipeline()


with st.sidebar:
    st.header("Model at a glance")
    try:
        report = json.loads((Path(__file__).resolve().parent.parent / "data" / "stage3_model" / "classification_report.json").read_text(encoding="utf-8"))
        m = report["test_metrics"]
        st.metric("Macro-F1 (cross-platform TEST)", f"{m['macro_f1']:.3f}")
        st.metric("MCC (cross-platform TEST)", f"{m['mcc']:.3f}")
        if m.get("roc_auc_ovr_macro") is not None:
            st.metric("ROC-AUC", f"{m['roc_auc_ovr_macro']:.3f}")
        st.caption(f"Trainable params: {report.get('trainable_params', '—'):,} (both backbones frozen)")
    except Exception:
        st.caption("Run notebook 09 to populate live headline metrics here.")
    st.divider()
    st.markdown(
        "**Four risk tiers**\n\n"
        "- 🟢 **Neutral** — no distress signal\n"
        "- 🟡 **Stress** — everyday stress / mild distress\n"
        "- 🟠 **Moderate** — clear, sustained distress\n"
        "- 🔴 **Crisis** — severe distress / self-harm signals"
    )

examples = [
    "Bahut akelapan mehsoos ho raha hai aajkal, kisi se baat karne ka mann nahi karta.",
    "Bas thoda tension hai kal exam ka, revise kar raha hoon.",
    "Life is so good today, went out with friends and had a great time!",
    "I don't want to live anymore, I just want it all to end.",
]

st.subheader("Try it")
choice = st.selectbox("Load an example (or type your own below):", ["— type your own —"] + examples)
default_text = "" if choice == "— type your own —" else choice
text = st.text_area("Post text (English / Hindi / Hinglish):", value=default_text, height=100,
                     placeholder="e.g. Aaj bahut pareshan hoon, kuch samajh nahi aa raha...")

now = datetime.datetime.now()
st.markdown("**Time of posting**")
st.caption(
    "The model fuses this alongside the text and an emotion signal — for some posts it turns out to "
    "matter more than the words themselves (see “How much did each signal actually drive this "
    "decision?” below). Defaults to right now; change it to see the prediction shift."
)
tcol1, tcol2 = st.columns(2)
with tcol1:
    post_date = st.date_input("Date", value=now.date())
with tcol2:
    post_time = st.time_input("Time", value=now.time())
post_dt = datetime.datetime.combine(post_date, post_time)
_is_weekend = post_dt.weekday() >= 5
_is_working_hour = 9 <= post_dt.hour < 18
st.caption(
    f"→ {post_dt.strftime('%A, %H:%M')} · "
    f"{'weekend' if _is_weekend else 'weekday'} · "
    f"{'inside' if _is_working_hour else 'outside'} the model's 9–18 working-hour window"
)

run = st.button("Analyze", type="primary", use_container_width=True)

if run:
    if not text.strip():
        st.warning("Type or select some text first.")
    else:
        pipeline = _load()
        with st.spinner("Running MuRIL + emotion embedding + DriftCapsNet forward pass..."):
            result = pipeline.predict_raw_text(text, dt=post_dt)
            lex_matches = pipeline.lexicon_matches(text)
        with st.spinner("Running 32-step Integrated Gradients (attributing every word)..."):
            ig_pairs, ig_target, ig_muril_text = pipeline.explain_integrated_gradients(text, dt=post_dt)
        with st.spinner("Measuring how much each signal stream drove this decision..."):
            stream_contrib, _ = pipeline.stream_contributions(text, dt=post_dt)

        tier = result["pred_tier"]
        color = TIER_COLORS[tier]
        st.markdown(
            f"<h2 style='color:{color};'>Predicted tier: {result['pred_label']} "
            f"({result['probs'][result['pred_label']]*100:.1f}% confidence)</h2>",
            unsafe_allow_html=True,
        )

        st.subheader("Tier probabilities")
        cols = st.columns(4)
        for i, col in enumerate(cols):
            label = TIER_NAMES[i]
            p = result["probs"][label]
            with col:
                st.metric(label, f"{p*100:.1f}%")
                st.progress(min(1.0, p))

        st.subheader("How much did each signal actually drive this decision?")
        text_share = stream_contrib["Text (your words)"]
        st.caption(
            "Word highlighting below explains the text stream's *own* behaviour, but this model fuses "
            "three streams (text, emotion, time-of-posting) and can end up leaning on one far more than "
            "the others for a given post — this is what closes that gap. Measured by zeroing one stream "
            "at a time and watching how much the predicted tier's score moves."
        )
        if text_share < 0.1:
            st.warning(
                f"⚠️ For this post, the **text stream contributed only {text_share*100:.0f}%** of the "
                "signal behind this prediction — the word highlighting below is real, but it is not "
                "the main reason the model landed on this tier. See the note below the chart."
            )
        stream_order = ["Text (your words)", "Emotion signal", "Time of posting"]
        stream_hues = {"Text (your words)": "#2a78d6", "Emotion signal": "#eb6834", "Time of posting": "#4a3aa7"}
        for name in stream_order:
            frac = stream_contrib[name]
            st.markdown(f"**{name}** — {frac*100:.0f}%")
            st.progress(min(1.0, frac))
        with st.expander("Why would text contribute so little?"):
            st.markdown(
                "This is a real, measured property of the currently trained checkpoint, not a demo bug: "
                "for many inputs the capsule-routing text pathway's output vector collapses to a very "
                "small magnitude before it reaches the fusion step, so the emotion-embedding and/or "
                "temporal-feature streams end up dominating the final decision almost regardless of what "
                "words were typed. It is consistent with — and a sharper, per-instance version of — the "
                "project's own ablation finding that removing the fusion streams entirely is the single "
                "largest effect measured in the whole study (Section 3.3/Figure 8): this model leans "
                "heavily on non-text signal. Retraining with a different capsule initialization or a "
                "stream-dropout regulariser is flagged as follow-up work, not attempted in this demo."
            )

        st.subheader(f"Why: which words pushed the model toward {TIER_NAMES[ig_target]}")
        st.caption(
            "Integrated Gradients (Sundararajan et al., 2017) — the exact method notebook 11 runs offline, "
            "here run live against your text. 32 steps from a zero-embedding baseline; every word gets a "
            f"signed score: how much it pushed the **{TIER_NAMES[ig_target]}** logit up (green) or down (red)."
        )

        if ig_pairs:
            max_abs = max(abs(v) for _, v in ig_pairs) or 1.0

            spans = []
            for w, v in ig_pairs:
                frac = min(1.0, abs(v) / max_abs)
                hue = "#1a8f3c" if v >= 0 else "#c0392b"
                alpha_bg = 12 + int(45 * frac)  # 0x0c..0x39
                spans.append(
                    f"<span title='IG={v:.2e}' style='background:{hue}{alpha_bg:02x};"
                    f"border-bottom:3px solid {hue};padding:2px 4px;margin:1px;border-radius:3px;"
                    f"display:inline-block;'>{w}</span>"
                )
            st.markdown(
                "<div style='line-height:2.4;font-size:16px;'>" + " ".join(spans) + "</div>",
                unsafe_allow_html=True,
            )
            st.caption(
                "🟢 green = pushed toward this tier · 🔴 red = pushed away · darker = stronger. "
                "Hover a word for its raw IG score."
            )

            st.markdown("**Top contributing words**")
            ranked = sorted(ig_pairs, key=lambda x: -abs(x[1]))[:8]
            for w, v in ranked:
                frac = min(1.0, abs(v) / max_abs)
                width = max(3, int(frac * 220))
                hue = "#1a8f3c" if v >= 0 else "#c0392b"
                direction = f"→ {TIER_NAMES[ig_target]}" if v >= 0 else f"⇢ away from {TIER_NAMES[ig_target]}"
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;margin:3px 0;'>"
                    f"<code style='width:110px;display:inline-block;background:{hue}22;padding:2px 6px;"
                    f"border-radius:4px;'>{w}</code>"
                    f"<div style='background:{hue};height:10px;width:{width}px;border-radius:3px;'></div>"
                    f"<span style='color:#888;font-size:12px;'>{direction}</span></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Text too short for word-level attribution.")

        st.markdown("**Clinical-lexicon corroboration** (Section 3.10's cross-checked signal)")
        st.caption(
            "The project's own results found this lexicon overlap more decisive than raw attribution "
            "scores alone (0% Neutral negative control → 12.5% Stress → 37.5% Moderate, Figure 11) — "
            "shown here as a second, independent check on the highlights above."
        )
        if lex_matches:
            chips = []
            for m in lex_matches:
                c = TIER_COLORS[m["tier"]]
                chips.append(
                    f"<span style='background:{c}22;border:1px solid {c};color:{c};padding:3px 10px;"
                    f"border-radius:14px;margin:3px;display:inline-block;font-weight:600;'>"
                    f"{m['term']} · {TIER_NAMES[m['tier']]}</span>"
                )
            st.markdown(" ".join(chips), unsafe_allow_html=True)
        else:
            st.caption(
                "No lexicon term matched — the prediction above rests on broader contextual/emotional "
                "signal rather than a specific clinical keyword (this is expected for many Neutral posts)."
            )

        with st.expander("Preprocessed text actually fed to MuRIL (transliterated)"):
            st.code(result["muril_text"])

st.divider()
st.caption(
    "This demo loads the already-trained Stage-A model checkpoint (data/stage3_model/model_state.pt) — "
    "no training happens in this app. Full methodology and evaluation: docs/ in this repository."
)
