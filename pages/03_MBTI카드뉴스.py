import streamlit as st
import pandas as pd
import hashlib

# ─────────────────────────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="MBTI 기질별 TOP10 카드뉴스", page_icon="🗺️", layout="wide")
st.title("🗺️ MBTI 기질별 TOP 10 — 카드 뉴스 스타일")
st.caption("NF / NT / SJ / SP / ST 별로 비율이 높은 나라 TOP10을 카드로 예쁘게 보여줘요. ✈️🍜🏰")

FILE_PATH = "countriesMBTI_16types.csv"

# ─────────────────────────────────────────────────────────────────
# 데이터 로드 & 전처리
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if "Country" not in df.columns:
        raise ValueError("CSV에 'Country' 컬럼이 없습니다.")

    mbti_cols = [c for c in df.columns if c != "Country"]
    # 숫자형으로 강제 변환
    df[mbti_cols] = df[mbti_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df, mbti_cols

try:
    df, mbti_cols = load_data(FILE_PATH)
except Exception as e:
    st.error(f"데이터 로드 에러: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────────
# 기질 그룹 정의
# SJ(ISTJ, ISFJ, ESTJ, ESFJ), SP(ISTP, ISFP, ESTP, ESFP),
# NF(INFJ, INFP, ENFJ, ENFP), NT(INTJ, INTP, ENTJ, ENTP),
# ST(ISTJ, ESTJ, ISTP, ESTP)  ← SJ와 SP에 걸쳐있는 ST 네 가지 합
# ─────────────────────────────────────────────────────────────────
GROUPS = {
    "NF": ["INFJ", "INFP", "ENFJ", "ENFP"],
    "NT": ["INTJ", "INTP", "ENTJ", "ENTP"],
    "SJ": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
    "SP": ["ISTP", "ISFP", "ESTP", "ESFP"],
    "ST": ["ISTJ", "ESTJ", "ISTP", "ESTP"],
}

# 각 그룹 합계를 컬럼으로 추가 (비율 합)
for g, cols in GROUPS.items():
    missing = [c for c in cols if c not in df.columns]
    if missing:
        st.error(f"{g} 그룹에 필요한 컬럼이 없습니다: {missing}")
        st.stop()
    df[g] = df[cols].sum(axis=1)

# ─────────────────────────────────────────────────────────────────
# 유틸: 이모지/색상 선택
# ─────────────────────────────────────────────────────────────────
emoji_pool = [
    "🏖️","🏙️","🏔️","🌋","🏜️","⛩️","🏰","🎎","🌉","🕌","🛕","🗼","🗽",
    "🌊","🌴","☕️","🍜","🍣","🥐","🌮","🍫","🍷","🍺","🍵","🍧","🍱","🥟"
]
def pick_emojis(key: str, k: int = 2):
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    e1 = emoji_pool[h % len(emoji_pool)]
    e2 = emoji_pool[(h // 7) % len(emoji_pool)]
    return [e1, e2] if e1 != e2 else [e1, "✨"]

# 라이트한 파스텔 백그라운드들
card_bg_colors = [
    "#FDF2F8", "#ECFEFF", "#F0F9FF", "#F0FDF4", "#FFF7ED",
    "#F5F5F5", "#FDF4FF", "#FEF2F2", "#FAFAF9", "#EFF6FF"
]

# ─────────────────────────────────────────────────────────────────
# 카드 렌더러
# ─────────────────────────────────────────────────────────────────
def render_top10_cards(group_key: str):
    """선택한 기질 그룹의 TOP10 나라를 카드 스타일로 뿌려줌"""
    if group_key not in GROUPS:
        st.warning("알 수 없는 그룹입니다.")
        return

    # 정렬 및 상위 10개
    top10 = (
        df[["Country", group_key]]
        .sort_values(group_key, ascending=False)
        .head(10)
        .reset_index(drop=True)
        .rename(columns={"Country": "국가", group_key: "ratio"})
    )
    top10["percent"] = (top10["ratio"] * 100).round(2)

    st.markdown(f"#### 🧭 {group_key}형이 많은 나라 TOP 10")
    st.caption("※ 비율은 해당 국가 인구 대비 해당 기질 그룹 합계(16유형 중 해당 그룹 4유형의 합)입니다.")

    # 2열 x 5행 카드 배치
    rows = [top10.iloc[i:i+2] for i in range(0, len(top10), 2)]
    for r_i, r_df in enumerate(rows):
        cols = st.columns(2, gap="large")
        for c_idx, (_, row) in enumerate(r_df.iterrows()):
            # 카드 스타일
            bg = card_bg_colors[(r_i*2 + c_idx) % len(card_bg_colors)]
            medal = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"][r_i*2 + c_idx]
            e1, e2 = pick_emojis(row["국가"])

            with cols[c_idx]:
                st.markdown(
                    f"""
                    <div style="
                        background:{bg};
                        border-radius:24px;
                        padding:18px 20px;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
                        border:1px solid rgba(0,0,0,0.05);
                    ">
                        <div style="font-size:28px; line-height:1.2; margin-bottom:6px;">
                            {medal} <b>{row['국가']}</b> {e1}{e2}
                        </div>
                        <div style="font-size:16px; color:#555; margin-bottom:6px;">
                            {group_key}형 비율
                        </div>
                        <div style="font-size:22px;"><b>{row['percent']}%</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with st.expander("🔎 표로 보기"):
        st.dataframe(
            top10[["국가", "percent"]].rename(columns={"percent": "비율(%)"}),
            use_container_width=True,
            hide_index=True
        )

# ─────────────────────────────────────────────────────────────────
# UI: 탭으로 그룹별 카드 보기
# ─────────────────────────────────────────────────────────────────
tabs = st.tabs(["🌸 NF", "🧠 NT", "🧾 SJ", "🎒 SP", "🧭 ST"])

with tabs[0]:
    render_top10_cards("NF")
with tabs[1]:
    render_top10_cards("NT")
with tabs[2]:
    render_top10_cards("SJ")
with tabs[3]:
    render_top10_cards("SP")
with tabs[4]:
    render_top10_cards("ST")

st.markdown("---")
st.caption(
    "📌 참고: ST형(ISTJ·ESTJ·ISTP·ESTP)은 SJ/SP에 걸쳐있는 4유형의 합계입니다. "
    "모든 값은 제공된 CSV의 비율(0~1)을 사용하며, 카드의 %는 해당 비율×100입니다. 🎈"
)
