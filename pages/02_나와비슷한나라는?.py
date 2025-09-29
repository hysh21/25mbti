import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib

# -------------------------------
# 페이지 기본 설정
# -------------------------------
st.set_page_config(page_title="당신과 비슷한 사람들이 많은 나라는?", page_icon="🌍", layout="wide")

st.title("🌍 당신과 비슷한 사람들이 많은 나라는?")
st.caption("MBTI를 선택하면, 그 유형의 비율이 높은 국가 TOP 7을 여행 추천처럼 보여드려요! ✈️🍜🏙️🏝️")

FILE_PATH = "countriesMBTI_16types.csv"

# -------------------------------
# 데이터 로드 & 전처리
# -------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df_ = pd.read_csv(path, encoding="utf-8-sig")
    df_.columns = df_.columns.str.strip()
    if "Country" not in df_.columns:
        raise ValueError("CSV에 'Country' 컬럼이 없습니다.")
    # MBTI 열만 숫자로 강제 변환
    mbti_cols_ = [c for c in df_.columns if c != "Country"]
    df_[mbti_cols_] = df_[mbti_cols_].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df_, mbti_cols_

try:
    df, mbti_cols = load_data(FILE_PATH)
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

# -------------------------------
# UI: MBTI 선택
# -------------------------------
# 보기 좋게 고정 순서(알파벳)로 정렬
mbti_types = sorted(mbti_cols)
default_mbti = "ENFP" if "ENFP" in mbti_types else mbti_types[0]

st.markdown("### 🧠 나의 MBTI를 골라주세요")
selected_mbti = st.selectbox("MBTI 선택", mbti_types, index=mbti_types.index(default_mbti))

# -------------------------------
# 계산: 선택 MBTI가 높은 국가 TOP 7
# -------------------------------
top7 = (
    df[["Country", selected_mbti]]
    .sort_values(by=selected_mbti, ascending=False)
    .head(7)
    .rename(columns={selected_mbti: "ratio"})
    .reset_index(drop=True)
)
top7["percent"] = (top7["ratio"] * 100).round(2)

# -------------------------------
# 시각 요소: 파스텔 팔레트 + 이모지
# -------------------------------
palette = (
    px.colors.qualitative.Set3
    + px.colors.qualitative.Pastel1
    + px.colors.qualitative.Pastel2
    + px.colors.qualitative.Safe
)
colors = palette[: len(top7)]

# 나라별로 귀여운 추천 이모지 뽑기(해시로 안정적 배정)
emoji_pool = ["🏖️", "🏙️", "🏔️", "🌋", "🏜️", "⛩️", "🏰", "🎎", "🌉", "🕌", "🛕", "🗼", "🗽", "🌊", "🌴", "☕️", "🍜", "🍣", "🥐", "🌮"]
def pick_emojis(name: str, k: int = 2):
    h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
    # 두 개 뽑되 서로 다르게
    e1 = emoji_pool[h % len(emoji_pool)]
    e2 = emoji_pool[(h // len(emoji_pool)) % len(emoji_pool)]
    return [e1, e2] if e1 != e2 else [e1, "✨"]

# -------------------------------
# 레이아웃: 좌(추천 리스트) / 우(막대그래프)
# -------------------------------
left, right = st.columns([0.58, 0.42])

with left:
    st.markdown(f"### ✈️ 여행처럼 추천할게요 — **{selected_mbti}** 와(과) 비슷한 사람들이 많은 나라 TOP 7")
    for i, row in top7.iterrows():
        rank_medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣"][i]
        e1, e2 = pick_emojis(row["Country"])
        st.markdown(
            f"{rank_medal} **{row['Country']}** — {row['percent']}%  {e1}{e2}",
            help="막대그래프에서 자세히 볼 수 있어요!"
        )

    with st.expander("🔎 표로 보기"):
        st.dataframe(
            top7[["Country", "percent"]].rename(columns={"Country": "국가", "percent": "비율(%)"}),
            use_container_width=True,
            hide_index=True
        )

with right:
    st.markdown("### 📊 TOP 7 막대그래프")
    chart = px.bar(
        top7.sort_values("percent", ascending=True),
        x="percent",
        y="Country",
        orientation="h",
        text="percent",
        color="Country",
        color_discrete_sequence=colors,
        labels={"percent": "비율(%)", "Country": "국가"},
        title=f"'{selected_mbti}' 비율이 높은 나라"
    )
    chart.update_traces(texttemplate="%{text}%", textposition="outside")
    chart.update_layout(
        showlegend=False,
        xaxis=dict(title="비율(%)"),
        yaxis=dict(title="국가"),
        margin=dict(l=80, r=40, t=80, b=40),
        height=520
    )
    st.plotly_chart(chart, use_container_width=True)

# -------------------------------
# 보너스: 설명 & 팁
# -------------------------------
st.markdown(
    """
    ---  
    ### 💡 사용 팁
    - 위의 셀렉트박스에서 **MBTI**를 바꾸면 추천 나라 TOP 7이 즉시 갱신됩니다.
    - 수치가 **비율(%)**로 표시되어 비교가 쉬워요.  
    - 데이터는 국가별 전체 인구 대비 해당 **MBTI 유형 비율**이며, 단순 재미·탐색용이에요. 🎈  
    """
)
