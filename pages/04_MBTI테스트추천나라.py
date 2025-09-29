import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(page_title="초간단 MBTI ✈️ 나라 추천", page_icon="🌍", layout="wide")
st.title("🌍 초간단 MBTI 테스트 → 당신과 비슷한 사람들이 많은 나라 추천")
st.caption("아주 간단한 8문항 테스트로 MBTI를 추정하고, 그 유형의 비율이 높은 상위 5개국을 여행지처럼 소개해드려요! 🎈")

FILE_PATH = "countriesMBTI_16types.csv"

# -------------------------------
# 데이터 로드 & 전처리
# -------------------------------
@st.cache_data
def load_mbti_data(path: str):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if "Country" not in df.columns:
        raise ValueError("CSV에 'Country' 컬럼이 없습니다.")

    mbti_cols = [c for c in df.columns if c != "Country"]
    # 숫자형 강제 변환 (문자·%·콤마 등 대응)
    df[mbti_cols] = df[mbti_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df, mbti_cols

try:
    df, mbti_cols = load_mbti_data(FILE_PATH)
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    st.stop()

# -------------------------------
# 초간단 MBTI 문항 (8문항: 각 축 2문항씩)
# 각 선택지는 해당 축의 한쪽에 +1
# -------------------------------
QUESTIONS = [
    # E vs I
    {
        "q": "주말엔 무엇이 더 에너지 충전이 돼요?",
        "opts": [("사람들과 어울리며 신나게! 🎉", "E"), ("혼자 조용히 쉬며 힐링 ☕️", "I")]
    },
    {
        "q": "새로운 모임에서 나는…",
        "opts": [("먼저 말 걸고 분위기를 띄워요 🗣️", "E"), ("관찰하며 천천히 적응해요 👀", "I")]
    },
    # S vs N
    {
        "q": "정보를 이해할 때 나는…",
        "opts": [("사실·경험 위주로! 구체적인 게 좋아요 📋", "S"), ("아이디어·가능성 상상! 큰 그림이 좋아요 🌈", "N")]
    },
    {
        "q": "설명서를 볼 때 내 스타일은?",
        "opts": [("순서대로 차근차근 따라하기 ✅", "S"), ("대략 파악하고 감으로 시도 🪄", "N")]
    },
    # T vs F
    {
        "q": "갈등 상황에서 나는…",
        "opts": [("원인·해결책을 논리적으로 정리 🧠", "T"), ("상대 감정을 먼저 헤아리기 💗", "F")]
    },
    {
        "q": "칭찬과 피드백 중 더 중요한 건?",
        "opts": [("정확한 피드백! 개선이 먼저 🔧", "T"), ("응원과 공감! 분위기가 먼저 🌟", "F")]
    },
    # J vs P
    {
        "q": "여행 계획은 어떻게?",
        "opts": [("일정표를 촘촘히! 계획이 편해요 🗓️", "J"), ("현지에서 즉흥적으로! 유연함이 좋아요 🎒", "P")]
    },
    {
        "q": "〆마감이 다가오면?",
        "opts": [("미리 끝내고 여유롭게 ✅", "J"), ("데드라인의 힘! 막판 집중 🚀", "P")]
    },
]

# -------------------------------
# 응답 수집
# -------------------------------
st.markdown("### 🧠 초간단 문항에 답해주세요")
with st.form("mini_mbti"):
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    for i, item in enumerate(QUESTIONS):
        label = f"{i+1}. {item['q']}"
        choice = st.radio(label, item["opts"], format_func=lambda x: x[0], index=None, key=f"q{i}")
        if choice is not None:
            scores[choice[1]] += 1

    submitted = st.form_submit_button("결과 보기 🔎")

def to_mbti(sc):
    # 각 축 비교해 MBTI 문자열 만들기
    ei = "E" if sc["E"] >= sc["I"] else "I"
    sn = "S" if sc["S"] >= sc["N"] else "N"
    tf = "T" if sc["T"] >= sc["F"] else "F"
    jp = "J" if sc["J"] >= sc["P"] else "P"
    return ei + sn + tf + jp

# 결과 계산
if submitted:
    if sum(scores.values()) == 0:
        st.warning("문항에 답해주세요! 🙂")
        st.stop()

    mbti = to_mbti(scores)
    st.success(f"당신의 (초간단) MBTI 추정 결과는 **{mbti}** 입니다! 🎉")

    # 해당 유형이 높은 나라 TOP5
    if mbti not in mbti_cols:
        st.error(f"데이터에 {mbti} 컬럼이 없습니다. CSV 헤더를 확인하세요.")
        st.stop()

    top5 = (
        df[["Country", mbti]]
        .sort_values(by=mbti, ascending=False)
        .head(5)
        .rename(columns={"Country":"국가", mbti:"ratio"})
        .reset_index(drop=True)
    )
    top5["percent"] = (top5["ratio"] * 100).round(2)

    st.markdown("---")
    st.markdown(f"### ✈️ {mbti} 와(과) 비슷한 사람들이 많은 나라 TOP 5")

    # 이모지 매핑(해시로 안정적·다양)
    emoji_pool = ["🏖️","🏙️","🏔️","🌋","🏜️","⛩️","🏰","🎎","🌉","🕌","🛕","🗼","🗽","🌊","🌴","☕️","🍜","🍣","🥐","🌮","🍫","🍻","🍵","🍧","🍱","🥟","🎡","🎨"]
    def pick_emojis(name: str, k: int = 2):
        h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
        e1 = emoji_pool[h % len(emoji_pool)]
        e2 = emoji_pool[(h // 7) % len(emoji_pool)]
        return [e1, e2] if e1 != e2 else [e1, "✨"]

    # 카드 1행 5개
    cols = st.columns(5, gap="large")
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    bg_colors = ["#FDF2F8","#ECFEFF","#F0F9FF","#F0FDF4","#FFF7ED"]

    for i, (_, row) in enumerate(top5.iterrows()):
        e1, e2 = pick_emojis(row["국가"])
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background:{bg_colors[i%len(bg_colors)]};
                    border-radius:20px;
                    padding:16px 14px;
                    box-shadow:0 6px 18px rgba(0,0,0,0.06);
                    border:1px solid rgba(0,0,0,0.05);
                    min-height:120px;
                ">
                    <div style="font-size:24px; margin-bottom:6px;">{medals[i]} <b>{row['국가']}</b> {e1}{e2}</div>
                    <div style="color:#666; font-size:14px; margin-bottom:4px;">{mbti} 비율</div>
                    <div style="font-size:20px;"><b>{row['percent']}%</b></div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 막대 그래프
    st.markdown("### 📊 상위 5개국 막대그래프")
    bar = px.bar(
        top5.sort_values("percent"),
        x="percent",
        y="국가",
        text="percent",
        orientation="h",
        color="국가",
        color_discrete_sequence=px.colors.qualitative.Set3 + px.colors.qualitative.Pastel1,
        labels={"percent":"비율(%)","국가":"국가"},
        title=f"{mbti} 비율이 높은 나라 TOP 5"
    )
    bar.update_traces(texttemplate="%{text}%", textposition="outside")
    bar.update_layout(showlegend=False, margin=dict(l=80,r=40,t=70,b=40), height=420)
    st.plotly_chart(bar, use_container_width=True)

    # 원본 표 보기
    with st.expander("🔎 원본 데이터 보기"):
        st.dataframe(
            top5[["국가","percent"]].rename(columns={"percent":"비율(%)"}),
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("아래 버튼을 눌러 결과를 확인해 보세요! (총 8문항) 🙂")
