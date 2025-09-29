import streamlit as st
import pandas as pd
import altair as alt

# 제목
st.title("🌍 MBTI 유형별 상위 10개 국가 시각화")

# 파일 읽기
file_path = "countriesMBTI_16types.csv"
df = pd.read_csv(file_path)

# MBTI 유형 리스트 (Country 제외)
mbti_types = [col for col in df.columns if col != "Country"]

# 사용자 선택
selected_type = st.selectbox("🔍 MBTI 유형을 선택하세요:", mbti_types)

# 선택한 유형 기준으로 정렬 후 상위 10개 추출
top10 = df[["Country", selected_type]].sort_values(by=selected_type, ascending=False).head(10)

# Altair 그래프 생성
chart = (
    alt.Chart(top10)
    .mark_bar(color="#4C9AFF")
    .encode(
        x=alt.X(selected_type, title=f"{selected_type} 비율"),
        y=alt.Y("Country", sort='-x', title="국가"),
        tooltip=["Country", selected_type]
    )
    .properties(
        title=f"🌟 {selected_type} 유형 비율이 높은 상위 10개 국가",
        width=600,
        height=400
    )
)

# 그래프 출력
st.altair_chart(chart, use_container_width=True)

# 데이터 표시
st.subheader(f"📋 {selected_type} 상위 10개 국가 데이터")
st.dataframe(top10.reset_index(drop=True))
