import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI by Country", page_icon="🌍", layout="wide")

st.title("🌍 나라를 고르면 MBTI 비율을 보여줄게요!")
st.caption("선택한 국가의 16개 MBTI 유형 비율을 한눈에 확인해보세요. 상단 셀렉트박스에서 나라를 선택하면 됩니다. 🧭")

# 1) 데이터 불러오기
FILE_PATH = "countriesMBTI_16types.csv"  # 같은 폴더에 위치
df = pd.read_csv(FILE_PATH)

# 방어 코드: Country 열이 존재하는지 확인
if "Country" not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다. 파일 형식을 확인해주세요.")
    st.stop()

# 2) UI - 국가 선택
countries = df["Country"].astype(str).sort_values().tolist()
default_country = "Korea, Republic of" if "Korea, Republic of" in countries else countries[0]
country = st.selectbox("🇺🇳 나라를 선택하세요", countries, index=countries.index(default_country))

# 3) 선택한 국가의 MBTI 시리즈 만들기 (컬럼명 안전하게 지정)
row = df.loc[df["Country"] == country]
if row.empty:
    st.error(f"선택한 국가({country})가 데이터에 없습니다.")
    st.stop()

series = row.iloc[0].drop(labels=["Country"])
data = series.reset_index()
# 여기서 확실히 컬럼명을 설정해 KeyError 방지!
data.columns = ["MBTI", "ratio"]
data = data.sort_values("ratio", ascending=False)
data["percent"] = (data["ratio"] * 100).round(2)

# 4) 예쁜 색 팔레트 (16개 이상 보장)
palette = (
    px.colors.qualitative.Set3
    + px.colors.qualitative.Pastel1
    + px.colors.qualitative.Pastel2
    + px.colors.qualitative.Safe
)
colors = palette[: len(data)]

# 5) Plotly 막대 그래프
fig = px.bar(
    data,
    x="percent",
    y="MBTI",
    orientation="h",
    color="MBTI",
    color_discrete_sequence=colors,
    hover_data={"ratio": False, "MBTI": True, "percent": True},
    labels={"percent": "비율(%)", "MBTI": "유형"},
    title=f"📊 {country} — MBTI 비율 Top to Bottom"
)

fig.update_traces(text=[f"{p}%" for p in data["percent"]], textposition="outside")

fig.update_layout(
    showlegend=False,
    xaxis=dict(title="비율(%)"),
    yaxis=dict(title="MBTI 유형", categoryorder="total ascending"),
    margin=dict(l=80, r=40, t=70, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# 6) 요약 박스: 상위 3개 유형
st.subheader("🏅 상위 3개 유형")
col1, col2, col3 = st.columns(3)
top3 = data.head(3).reset_index(drop=True)
with col1:
    st.metric(f"🥇 {top3.loc[0,'MBTI']}", f"{top3.loc[0,'percent']}%")
with col2:
    st.metric(f"🥈 {top3.loc[1,'MBTI']}", f"{top3.loc[1,'percent']}%")
with col3:
    st.metric(f"🥉 {top3.loc[2,'MBTI']}", f"{top3.loc[2,'percent']}%")

# 7) 원본 데이터(선택국가) 표
with st.expander("🔎 원본 데이터 (선택 국가의 16유형 비율 표 보기)"):
    st.dat
