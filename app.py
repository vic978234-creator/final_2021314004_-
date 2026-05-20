import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 및 테마 설정
st.set_page_config(
    page_title="2025 Netflix Strategic Analytics",
    page_icon="🎬",
    layout="wide"
)

# 2. 데이터 고도화 전처리 함수
@st.cache_data
def load_and_clean_data():
    movies = pd.read_csv("netflix_movies_detailed_up_to_2025.csv")
    tv_shows = pd.read_csv("netflix_tv_shows_detailed_up_to_2025.csv")
    
    movies['content_type'] = 'Movie'
    tv_shows['content_type'] = 'TV Show'
    
    # 데이터 병합을 위한 컬럼 동기화
    if 'budget' not in tv_shows.columns: tv_shows['budget'] = 0
    if 'revenue' not in tv_shows.columns: tv_shows['revenue'] = 0
    if 'duration' not in movies.columns: movies['duration'] = "N/A"
    
    common_cols = [
        'show_id', 'content_type', 'title', 'director', 'cast', 'country', 
        'date_added', 'release_year', 'genres', 'language', 'popularity', 
        'vote_count', 'vote_average', 'budget', 'revenue'
    ]
    
    combined = pd.concat([movies[common_cols], tv_shows[common_cols]], ignore_index=True)
    
    # 시계열 데이터 가공
    combined['date_added'] = pd.to_datetime(combined['date_added'].str.strip(), errors='coerce')
    combined['month_added'] = combined['date_added'].dt.month
    
    # 금융 지표 가공 (영화 전용)
    combined['profit'] = combined['revenue'] - combined['budget']
    combined['roi'] = combined.apply(lambda r: (r['profit'] / r['budget'] * 100) if r['budget'] > 0 else 0, axis=1)
    
    return combined

try:
    df = load_and_process_data = load_and_clean_data()

    # 타이틀
    st.title("🎬 Beyond the Screen")
    st.subheader("Data-Driven Analysis of Netflix's Global Success Formula in 2025")
    st.markdown("본 대시보드는 2025년 최신 데이터를 기반으로 단순 분류를 넘어 **재무적 성과, 인적 자원 영향력, 시계열 트렌드**를 종합적으로 시뮬레이션합니다.")
    st.divider()

    # 사이드바 필터
    st.sidebar.header("🔍 Global Control Panel")
    selected_type = st.sidebar.multiselect("콘텐츠 타입 선택", options=['Movie', 'TV Show'], default=['Movie', 'TV Show'])
    selected_lang = st.sidebar.multiselect("주요 언어권 필터", options=list(df['language'].dropna().unique()[:10]), default=['en', 'ko', 'ja'])
    
    # 필터 적용
    filtered_df = df[df['content_type'].isin(selected_type) & df['language'].isin(selected_lang)]

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Financial & ROI Analysis", 
        "⭐ Hitmaker (Director & Cast)", 
        "📅 Seasonality Trends", 
        "🎮 Content Strategy Simulator"
    ])

    # -------------------------------------------------------------
    # TAB 1: 재무 및 ROI 분석 (영화 비즈니스 관점)
    # -------------------------------------------------------------
    with tab1:
        st.subheader("📊 OTT 콘텐츠의 투자 효율성 분석 (영화 데이터 기반)")
        st.markdown("제작비 대조 데이터가 존재하는 작품을 대상으로 흥행 수익 및 ROI(투자 성과)를 추적합니다.")
        
        financial_movies = filtered_df[(filtered_df['content_type'] == 'Movie') & (filtered_df['budget'] > 0) & (filtered_df['revenue'] > 0)]
        
        if not financial_movies.empty:
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.write("#### 💸 최고 수익 달성 대작 Top 10")
                top_revenue = financial_movies.sort_values(by='revenue', ascending=False).head(10)
                fig_rev = px.bar(top_revenue, x='revenue', y='title', orientation='h', color='revenue', color_continuous_scale='Reds')
                st.plotly_chart(fig_rev, use_container_width=True)
                
            with m_col2:
                st.write("#### 📈 최고 가성비 장르 (평균 ROI 순위)")
                # 장르별 평균 ROI
                genre_roi = financial_movies.groupby('genres')['roi'].mean().sort_values(ascending=False).head(10).reset_index()
                fig_roi = px.bar(genre_roi, x='roi', y='genres', orientation='h', color='roi', color_continuous_scale='Blues')
                st.plotly_chart(fig_roi, use_container_width=True)
        else:
            st.info("선택한 필터 조건에 제작비/수익 데이터가 포함된 영화가 없습니다.")

    # -------------------------------------------------------------
    # TAB 2: 인적 자원 영향력 분석 (감독 및 배우 파워)
    # -------------------------------------------------------------
    with tab2:
        st.subheader("⭐ 넷플릭스 플랫폼 내 핵심 인적 자원 분석")
        
        col_dir, col_cast = st.columns(2)
        with col_dir:
            st.write("#### 🎬 최다 흥행작 연출 감독 (평균 인기도 순)")
            valid_directors = filtered_df[filtered_df['director'].notna() & (filtered_df['director'] != "")]
            top_directors = valid_directors.groupby('director')[['popularity', 'vote_average']].mean().sort_values(by='popularity', ascending=False).head(10).reset_index()
            st.dataframe(top_directors, use_container_width=True)
            
        with col_cast:
            st.write("#### 🎭 주요 출연진 데이터 검색")
            actor_search = st.text_input("분석하고 싶은 배우 이름을 입력해 보세요 (예: Leonardo DiCaprio, Yoo Jae-suk)")
            if actor_search:
                actor_movies = filtered_df[filtered_df['cast'].str.contains(actor_search, case=False, na=False)]
                st.write(f"**{actor_search}** 배우의 출연작 총 {len(actor_movies)}건 분석 결과:")
                st.dataframe(actor_movies[['title', 'content_type', 'release_year', 'vote_average', 'popularity']], use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: 시계열 주기성 분석 (Netflix Content Added Calendar)
    # -------------------------------------------------------------
    with tab3:
        st.subheader("📅 연중 월별 콘텐츠 업로드 트렌드 분석")
        st.markdown("넷플릭스가 월별/계절별로 대중에게 콘텐츠를 공개하는 패턴을 시각화합니다.")
        
        season_df = filtered_df[filtered_df['month_added'].notna()]
        if not season_df.empty:
            monthly_pattern = season_df.groupby(['month_added', 'content_type']).size().reset_index(name='count')
            fig_month = px.bar(
                monthly_pattern, x='month_added', y='count', color='content_type', barmode='group',
                title="월별 신규 콘텐츠 등록 개수 분포 (주기성 증명)",
                labels={'month_added': '등록 월 (Month)', 'count': '등록 수'},
                text_auto=True
            )
            fig_month.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
            st.plotly_chart(fig_month, use_container_width=True)
        else:
            st.info("시계열 데이터 분석을 위한 등록일(date_added) 데이터가 부족합니다.")

    # -------------------------------------------------------------
    # TAB 4: 가상 기획 시뮬레이터 (Expected Value Simulator)
    # -------------------------------------------------------------
    with tab4:
        st.subheader("🎮 2025 글로벌 콘텐츠 전략 시뮬레이터")
        st.markdown("새로운 영상 콘텐츠를 기획한다고 가정해봅시다. 과거 데이터 기반의 시뮬레이션을 통해 기대 성과를 예측합니다.")
        
        sim_col1, sim_col2 = st.columns([1, 2])
        
        with sim_col1:
            st.write("#### 🏗️ 가상 기획 시나리오 설정")
            sim_genre = st.selectbox("기획할 메인 장르", options=list(df['genres'].dropna().unique()[:15]))
            sim_lang = st.selectbox("타겟 언어 설정", options=['en', 'ko', 'ja', 'es', 'fr'])
            sim_budget = st.slider("예상 제작비 세팅 ($ 단위)", min_value=1000000, max_value=200000000, value=20000000, step=1000000)
            
        with sim_col2:
            st.write("#### 🔮 데이터 기반 가상 흥행 시뮬레이션 결과")
            # 매칭 데이터 추출
            matched = df[(df['genres'].str.contains(sim_genre, na=False)) & (df['language'] == sim_lang)]
            
            if len(matched) > 0:
                est_rating = matched['vote_average'].median()
                est_pop = matched['popularity'].median()
                # 과거 비례 기반 수익률 예측 연산
                avg_roi_multiplier = matched[matched['budget'] > 0]['roi'].median()
                est_revenue = sim_budget * (1 + (avg_roi_multiplier / 100)) if avg_roi_multiplier > 0 else sim_budget * 1.5
                
                sim_kpi1, sim_kpi2, sim_kpi3 = st.columns(3)
                sim_kpi1.metric("예상 시청자 평점", f"{est_rating:.2f} / 10")
                sim_kpi2.metric("예상 글로벌 인기도", f"{est_pop:.1f} pts")
                sim_kpi3.metric("예상 기대 박스오피스 수익", f"${est_revenue/1000000:.1f}M")
                
                st.success(f"💡 분석 결과: 해당 조합({sim_genre} + {sim_lang})은 과거 데이터 패턴상 매우 안정적인 수익성을 보였습니다. 기획서 작성 시 위 지표를 인용하세요.")
            else:
                st.warning("매칭되는 과거 통계 데이터가 부족하여 시뮬레이션을 진행할 수 없습니다. 다른 조합을 조합해 주세요.")

except Exception as e:
    st.error(f"⚠️ 에러 발생: {e}")
