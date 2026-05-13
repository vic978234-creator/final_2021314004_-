import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    # 파일이 업로드되어 있다고 가정하거나, URL을 통해 가져옵니다.
    df = pd.read_csv("netflix_titles.csv")
    return df

try:
    df = load_data()
    st.title("🎬 Netflix Global Content Dashboard")
    
    # 사이드바 필터
    country = st.sidebar.multiselect("국가 선택", options=df['country'].unique(), default=["South Korea"])
    
    # 시각화
    filtered_df = df[df['country'].isin(country)]
    fig = px.bar(filtered_df.groupby('type').size().reset_index(name='count'), x='type', y='count', color='type')
    st.plotly_chart(fig)
    
    st.dataframe(filtered_df)
except Exception as e:
    st.error(f"데이터 파일(netflix_titles.csv)이 저장소에 있는지 확인해주세요!")
