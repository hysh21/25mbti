import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI by Country", page_icon="🌍", layout="wide")
st.title("MBTI 비율: 국가별 보기 🌍")
st.caption("국가를 선택하면 16개 MBTI 유형 비율을 보여줍니다. 🧭")

FILE_PATH = "countriesMBTI_16types.csv"
df = pd.read_csv(FILE_PATH, encoding="utf-8-sig")
df.columns = df.columns.str.strip()

if "Country" not in df.columns:
    st.error("'Country' 컬럼이 없습니다. CSV 헤더를 확인하세요.")
    st.stop()

mbti_cols = [c for c in df.columns if c != "Country"]
df[mbti_cols] = df[mbti_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

countries = df["Country"].astype(str).sort_values().tolist()
default_country = "Korea, Republic of" if "Korea, Republic of" in countries else countries[0]
country = st.selectbox("나라 선택", countries, index=countries.index(default_country))

row = df.loc[df["Country"] == country]
if row.empty:
    st.error(f"{country} 가 데이터에 없습니다.")
    st.stop()

series = row.iloc[0].drop(labels=["Country"])
data = series.reset_index()
data.columns = ["MBTI", "ratio"]

# ← 문제 해결 포인트
if data["ratio"].dtype == "object":
    data["ratio"] = (
        data["ratio"].astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
data["ratio"] = pd.to_numeric(data["ratio"], errors="coerce")

if data["ratio"].isna().all():
    st.error("비율 값이 모두 숫자가 아닙니다. CSV의 값(%, 공백, 콤마 등)을 확인해주세요.")
    st.stop()

data = data.sort_values("ratio", ascending=False)
data["percent"] = (data["ratio"] * 100).round(2)

palette = (
    px.colors.qualitative.Set3
    + px.colors.qualitative.Pastel1
    + px.colors.qualitative.Pastel2
    + px.colors.qualitative.Safe
)
colors = palette[: len(data)]

fig = px.bar(
    data,
    x="percent",
    y="MBTI",
    orientation="h",
    color="MBTI",
    color_discrete_sequence=colors,
    hover_data={"ratio": False, "MBTI": True, "percent": True},
    labels={"percent": "비율(%)", "MBTI": "유형"},
    title=f"{country} — MBTI 비율"
)
fig.update_traces(text=[f"{p}%" for p in data["percent"]], textposition="outside")
fig.update_layout(showlegend=False, yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig, use_container_width=True)

st.subheader("상위 3개 유형 🏅")
top3 = data.head(3).reset_index(drop=True)
c1, c2, c3 = st.columns(3)
c1.metric(top3.loc[0, "MBTI"], f"{top3.loc[0, 'percent']}%")
c2.metric(top3.loc[1, "MBTI"], f"{top3.loc[1, 'percent']}%")
c3.metric(top3.loc[2, "MBTI"], f"{top3.loc[2, 'percent']}%")

with st.expander("원본 값 보기"):
    st.dataframe(data[["MBTI", "percent"]].rename(columns={"percent": "비율(%)"}), use_container_width=True)
