import streamlit as st
import pandas as pd

# 제목
st.title("🌍 MBTI 유형별 국가 데이터 미리보기")

# 파일 읽기
file_path = "countriesMBTI_16types.csv"  # 같은 폴더에 있다고 가정
df = pd.read_csv(file_path)

# 데이터 미리보기
st.subheader("📋 데이터 상위 5줄 미리보기")
st.dataframe(df.head())

# 간단한 정보 요약
st.write("✅ 전체 행 개수:", df.shape[0])
st.write("✅ 전체 열 개수:", df.shape[1])
