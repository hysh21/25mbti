import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI by Country", page_icon="🌍", layout="wide")

st.title("🌍 나라를 고르면 MBTI 비율을 보여줄게요!")
st.caption("선택한 국가의 16개 MBTI 유형 비율을 한눈에 확인해보세요. 상단 셀렉트박스에서 나라를 선택하면 됩니다. 🧭")

# 1) 데이터 불러오기
FILE_PATH = "countriesMBTI_16types.csv"
df = pd.read_csv(FILE_PATH)

# --- 열 이름 공백 제거(예방) ---
df.columns = df.columns.str.strip()

# --- Country 존재 확인 ---
if "Country" not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다. 파일 형식을 확인해주세요.")
    st.stop()

# --- MBTI 열을 모두 숫자로 강제 변환(문자 -> 숫자), 변환 실패는 NaN -> 0 ---
mbti_cols = [c for c in df.columns if c != "Country"]
df[mbti_cols] = df[mbti_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

# 2) UI - 국가 선택
countries = df["Country"].astype(str).sort_values().tolist()
default_country = "Korea, Republic of" if "Korea, Republic of" in countries else countries[0]
country = st.selectbox("🇺🇳 나라를 선택하세요", countries, index=countries.index(default_country))

# 3) 선택한 국가의 MBTI 시리즈 만들기
row = df.loc[df["Country"] == country]
if row.empty:
    st.error(f"선택한 국가({country})가 데이터에 없습니다.")
    st.stop()

series = row.iloc[0].drop(labels=["Country"])
data = series.reset_index()
data.columns = ["MBTI", "ratio"]  # 확실히 컬럼명 지정
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
    y="MBT
