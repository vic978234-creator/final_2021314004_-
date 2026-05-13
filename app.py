import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="2025 Netflix Global Insight", layout="wide")
st.title("🎬 2025 Netflix Global Strategic Dashboard")
st.markdown("본 대시보드는 2025년 최신 데이터를 바탕으로 콘텐츠의 상업적 가치와 시청자 선호도를 다각도로 분석합니다.")

# 2. 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 두 개의 파일을 각각 읽어옵니다.
    movies_df = pd.read_csv("netflix_movies_detailed_up_to_2025.csv")
    tv_df = pd.read_csv("netflix_tv_shows_detailed_up_to_2025.csv")
    
    # 데이터 통합을 위해 공통 컬럼 설정
    movies_df['content_type'] = 'Movie'
    tv_df['content_type'] = 'TV Show'
    
    # 두 데이터프레임 합치기
    combined = pd.concat([movies_df, tv_df], ignore_index=True)
    return combined

try:
    df = load_data()

    # --- [사이드바 필터] ---
    st.sidebar.header("🔍 분석 필터")
    
    # 1. 콘텐츠 타입 선택
    c_type = st.sidebar.multiselect("콘텐츠 타입", options=['Movie', 'TV Show'], default=['Movie', 'TV Show'])
    
    # 2. 장르 필터 (복수 장르 대응)
    all_genres = set()
    df['genres'].dropna().str.split(', ').apply(all_genres.update)
    selected_genres = st.sidebar.multiselect("장르 선택", options=sorted(list(all_genres)))

    # 필터링 로직
    filtered_df = df[df['content_type'].isin(c_type)]
    if selected_genres:
        filtered_df = filtered_df[filtered_df['genres'].str.contains('|'.join(selected_genres), na=False)]

    # --- [섹션 1: 데이터 요약 통계 (KPI)] ---
    st.subheader("📌 데이터 요약")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 콘텐츠 수", f"{len(filtered_df):,}개")
    with col2:
        st.metric("평균 평점", f"{filtered_df['vote_average'].mean():.2f} / 10")
    with col3:
        st.metric("평균 인기도", f"{filtered_df['popularity'].mean():.2f}")
    with col4:
        # 영화 데이터에만 있는 Budget 정보 활용 (Movie 선택 시에만 유효)
        if 'budget' in filtered_df.columns and filtered_df['budget'].sum() > 0:
            avg_budget = filtered_df[filtered_df['budget'] > 0]['budget'].mean()
            st.metric("평균 제작비 (Movies)", f"${avg_budget/1000000:.1f}M")
        else:
            st.metric("최다 제작 국가", filtered_df['country'].mode()[0] if not filtered_df['country'].empty else "N/A")

    st.divider()

    # --- [섹션 2: 심화 분석 시각화] ---
    tab1, tab2, tab3 = st.tabs(["💡 상관관계 분석", "🌍 글로벌 언어/국가", "📉 장르별 성과"])

    with tab1:
        st.subheader("인기도와 평점의 상관관계 (Scatter Plot)")
        # 인기도(상업성)와 평점(작품성) 사이의 관계를 시각화
        fig_scatter = px.scatter(
            filtered_df, x="vote_average", y="popularity", 
            color="content_type", hover_name="title", size="popularity",
            title="상업적 인기도와 시청자 평점의 비례 관계 분석",
            labels={"vote_average": "평점", "popularity": "인기도"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("주요 사용 언어 분포")
            lang_data = filtered_df['language'].value_counts().head(10)
            fig_pie = px.pie(values=lang_data.values, names=lang_data.index, hole=0.4, title="상위 10개 언어 비중")
            st.plotly_chart(fig_pie)
        with col_b:
            st.subheader("연도별 콘텐츠 출시 트렌드")
            trend = filtered_df.groupby(['release_year', 'content_type']).size().reset_index(name='count')
            fig_line = px.line(trend[trend['release_year'] > 2010], x='release_year', y='count', color='content_type', markers=True)
            st.plotly_chart(fig_line)

    with tab3:
        st.subheader("장르별 평균 평점 상위 분석")
        # 장르별로 데이터를 쪼개서 평균 평점 계산 (영상학적 접근)
        genre_rating = filtered_df.groupby('genres')['vote_average'].mean().sort_values(ascending=False).head(15).reset_index()
        fig_bar = px.bar(genre_rating, x='vote_average', y='genres', orientation='h', color='vote_average',
                         title="어떤 장르가 시청자에게 높은 평가를 받는가?")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- [섹션 3: 상세 데이터 검색] ---
    st.divider()
    st.subheader("🔍 데이터 상세 검색")
    search = st.text_input("찾고 싶은 작품 제목을 입력하세요:")
    if search:
        results = filtered_df[filtered_df['title'].str.contains(search, case=False, na=False)]
        st.write(f"검색 결과: {len(results)}건")
        st.dataframe(results)
    else:
        st.write("하단에서 전체 필터링된 데이터를 확인할 수 있습니다.")
        st.dataframe(filtered_df.head(100))

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다. 파일명을 확인해주세요: {e}")
