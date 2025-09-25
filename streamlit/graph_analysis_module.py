import streamlit as st  
import pymysql  
import pandas as pd  
import numpy as np  
import plotly.express as px  
import plotly.graph_objects as go  
from plotly.subplots import make_subplots  
import plotly.figure_factory as ff  
import os  
from dotenv import load_dotenv

# 환경변수 로드  
load_dotenv()

# 데이터베이스 연결 함수  
def get_db_connection():  
    try:  
        connection = pymysql.connect(  
            host= os.getenv('DB_HOST'),  
            user= os.getenv('DB_USER'),  
            passwd= os.getenv('DB_PASSWORD'),  
            database= os.getenv('DB_NAME')  
            )  
        return connection  
    except Exception as e:  
        st.error(f"데이터베이스 연결 실패: {e}")  
        return None

# 고급 데이터 처리 함수  
def get_advanced_yearly_data():  
    connection = get_db_connection()  
    if not connection:  
        return None  
     
    try:  
        # 친환경차량 데이터  
        eco_query = """  
        SELECT  
            d.year,  
            SUM(e.ev) as ev,  
            SUM(e.hev) as hev,  
            SUM(e.fcev) as fcev,  
            SUM(e.cng) as cng,  
            SUM(e.etc) as etc,  
            SUM(e.ev + e.hev + e.fcev + e.cng + e.etc) as total_eco  
        FROM dim_monthly d  
        JOIN eco_monthly e ON d.date_key = e.date_key  
        WHERE d.year BETWEEN 2015 AND 2024  
        GROUP BY d.year  
        ORDER BY d.year  
        """  
         
        eco_df = pd.read_sql(eco_query, connection)  
         
        # 내연기관차량 데이터  
        ice_query = """  
        SELECT  
            d.year,  
            SUM(i.gasoline) as gasoline,  
            SUM(i.diesel) as diesel,  
            SUM(i.lpg) as lpg,  
            SUM(i.gasoline + i.diesel + i.lpg) as total_ice  
        FROM dim_monthly d  
        JOIN ice_monthly i ON d.date_key = i.date_key  
        WHERE d.year BETWEEN 2015 AND 2024  
        GROUP BY d.year  
        ORDER BY d.year  
        """  
         
        ice_df = pd.read_sql(ice_query, connection)  
         
        # 데이터 병합  
        df = pd.merge(eco_df, ice_df, on='year')  
        df['total_cars'] = df['total_eco'] + df['total_ice']  
        df['eco_ratio'] = (df['total_eco'] / df['total_cars'] * 100).round(1)  
        df['ice_ratio'] = (df['total_ice'] / df['total_cars'] * 100).round(1)
        
        # 10년간 누적 비율 계산
        total_eco_cumulative = df['total_eco'].sum()
        total_cars_cumulative = df['total_cars'].sum()
        cumulative_eco_ratio = (total_eco_cumulative / total_cars_cumulative * 100).round(1)
         
        connection.close()  
        return df, cumulative_eco_ratio
         
    except Exception as e:  
        st.error(f"데이터 조회 실패: {e}")  
        connection.close()  
        return None

def show_graph_analysis():  
    """고급 라이브러리를 사용한 그래프 분석 페이지"""  
     
    st.markdown("""  
    <div class="hero-section">  
        <h1 class="hero-title">📊 고급 그래프 분석 (Plotly + Pandas)</h1>  
        <p class="hero-subtitle">Plotly, Pandas, Numpy를 활용한 인터랙티브 데이터 시각화</p>  
    </div>  
    """, unsafe_allow_html=True)  
     
    # 데이터 로딩  
    with st.spinner("고급 분석을 위한 데이터 처리 중..."):  
        result = get_advanced_yearly_data()
        if result is not None:
            df, cumulative_eco_ratio = result
        else:
            df, cumulative_eco_ratio = None, None
     
    if df is not None and not df.empty:  
         
        # 고급 메트릭 대시보드  
        st.subheader("📊 연도별 등록 현황 요약 (친환경 vs 내연기관)")  
         
        col1, col2, col3, col4, col5 = st.columns(5)  
         
        latest_year = df['year'].max()  
        latest_data = df[df['year'] == latest_year].iloc[0]  
         
        with col1:  
            eco_value = f"{latest_data['total_eco'] / 1000:.0f}대"
            eco_delta = f"{(latest_data['total_eco'] - df[df['year'] == latest_year-1]['total_eco'].iloc[0]) / 1000:+.0f}대"
            st.metric(  
                label="최근년 친환경차량",  
                value=eco_value,  
                delta=eco_delta  
            )
            st.caption("(단위:천)")
         
        with col2:  
            ice_value = f"{latest_data['total_ice'] / 1000:.0f}대"
            ice_delta = f"{(latest_data['total_ice'] - df[df['year'] == latest_year-1]['total_ice'].iloc[0]) / 1000:+.0f}대"
            st.metric(  
                label="최근년 내연기관",  
                value=ice_value,  
                delta=ice_delta  
            )
            st.caption("(단위:천)")
         
        with col3:  
            prev_year_ratio = df[df['year'] == latest_year-1]['eco_ratio'].iloc[0] if latest_year > df['year'].min() else 0
            current_year_ratio = latest_data['eco_ratio']
            cumulative_delta = cumulative_eco_ratio - (df[df['year'] == latest_year-1]['total_eco'].sum() / df[df['year'] == latest_year-1]['total_cars'].sum() * 100) if latest_year > df['year'].min() else 0
            
            st.metric(  
                label="누적 친환경 비율",  
                value=f"{cumulative_eco_ratio:.1f}%",  
                delta=f"{cumulative_delta:+.1f}%"  
            )
         
        with col4:  
            growth_rate = ((latest_data['total_eco'] / df['total_eco'].iloc[0]) - 1) * 100  
            st.metric(  
                label="15-24 성장률",  
                value=f"{growth_rate:.0f}%",  
                delta="10년간"  
            )  
         
        with col5:  
            avg_growth = df['total_eco'].pct_change().mean() * 100  
            st.metric(  
                label="평균 연성장률",  
                value=f"{avg_growth:.1f}%",  
                delta="친환경차량"  
            )  
         
        st.markdown("---")  
         
        # 1. 인터랙티브 트렌드 분석  
        st.subheader("📈 친환경차 등록 추이와 비율 변화")  
         
        col1, col2 = st.columns(2)  
         
        with col1:  
            # Plotly 막대 차트 - 친환경차량 추이  
            fig_bar = px.bar(  
                df,  
                x='year',  
                y='total_eco',  
                title='친환경차량 등록 추이',  
                labels={'year': '연도', 'total_eco': '등록대수 (대)'},  
                color='total_eco',  
                color_continuous_scale='Viridis',  
                text='total_eco'  
            )  
            fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')  
            fig_bar.update_layout(  
                showlegend=False,  
                height=400,  
                xaxis_tickangle=0,  
                title_font_size=16  
            )  
            st.plotly_chart(fig_bar, use_container_width=True)  
         
        with col2:  
            # Plotly 라인 차트 - 비율 변화  
            fig_line = px.line(  
                df,  
                x='year',  
                y='eco_ratio',  
                title='친환경차량 비율 변화',  
                labels={'year': '연도', 'eco_ratio': '비율 (%)'},  
                markers=True,  
                line_shape='spline'  
            )  
            fig_line.update_traces(  
                line_color='#2E86AB',  
                marker_size=8,  
                marker_color='#A23B72'  
            )  
            fig_line.update_layout(  
                height=400,  
                xaxis_tickangle=0,  
                title_font_size=16,  
                yaxis_range=[0, df['eco_ratio'].max() * 1.1]  
            )  
            st.plotly_chart(fig_line, use_container_width=True)  
         
        # 2. 고급 stacked bar chart  
        st.subheader("🔄 연도별 전체 차량 등록 누적 비교")  
         
        fig_stacked = go.Figure()  
         
        fig_stacked.add_trace(go.Bar(  
            x=df['year'],  
            y=df['total_ice'],  
            name='내연기관차량',  
            marker_color='#FF6B6B',  
            text=df['total_ice'],  
            texttemplate='%{text:,.0f}',  
            textposition='inside'  
        ))  
         
        fig_stacked.add_trace(go.Bar(  
            x=df['year'],  
            y=df['total_eco'],  
            name='친환경차량',  
            marker_color='#4ECDC4',  
            text=df['total_eco'],  
            texttemplate='%{text:,.0f}',  
            textposition='inside'  
        ))  
         
        fig_stacked.update_layout(  
            barmode='stack',  
            title='연도별 차량 등록 현황 (누적)',  
            xaxis_title='연도',  
            yaxis_title='등록대수 (대)',  
            height=500,  
            xaxis_tickangle=0,  
            title_font_size=18,  
            legend=dict(  
                orientation="h",  
                yanchor="bottom",  
                y=1.02,  
                xanchor="right",  
                x=1  
            )  
        )  
         
        st.plotly_chart(fig_stacked, use_container_width=True)  
         
        # 3. 차종별 상세 분석 (1x2)  
        st.subheader("🚗 차종별 등록 현황 (전기·하이브리드·수소 vs 가솔린·디젤·LPG)")  
         
        fig_detail = make_subplots(  
            rows=1, cols=2,  
            subplot_titles=('친환경차량 상세 분류', '내연기관차량 상세 분류'),  
            specs=[[{"type": "bar"}, {"type": "bar"}]]  
        )  
         
        # 친환경차량 상세 분류  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['ev'], name='전기차', marker_color='#1f77b4'),  
            row=1, col=1  
        )  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['hev'], name='하이브리드', marker_color='#ff7f0e'),  
            row=1, col=1  
        )  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['fcev'], name='수소차', marker_color='#2ca02c'),  
            row=1, col=1  
        )  
         
        # 내연기관차량 상세 분류  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['gasoline'], name='가솔린', marker_color='#d62728'),  
            row=1, col=2  
        )  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['diesel'], name='디젤', marker_color='#9467bd'),  
            row=1, col=2  
        )  
        fig_detail.add_trace(  
            go.Bar(x=df['year'], y=df['lpg'], name='LPG', marker_color='#8c564b'),  
            row=1, col=2  
        )  
         
        fig_detail.update_layout(height=500, title_text="차종별 상세 분석", title_font_size=18)  
        fig_detail.update_xaxes(tickangle=45)  
         
        st.plotly_chart(fig_detail, use_container_width=True)  
         
        # 4. 변화 트렌드 분석 (1x2)  
        st.subheader("📉 연도별 비율 변화와 성장률 추이")  
         
        fig_trend = make_subplots(  
            rows=1, cols=2,  
            subplot_titles=('비율 변화 트렌드', '성장률 분석'),  
            specs=[[{"type": "scatter"}, {"type": "scatter"}]]  
        )  
         
        # 비율 변화  
        fig_trend.add_trace(  
            go.Scatter(x=df['year'], y=df['eco_ratio'], mode='lines+markers',  
                      name='친환경 비율', line_color='green'),  
            row=1, col=1  
        )  
        fig_trend.add_trace(  
            go.Scatter(x=df['year'], y=df['ice_ratio'], mode='lines+markers',  
                      name='내연기관 비율', line_color='red'),  
            row=1, col=1  
        )  
         
        # 성장률 분석  
        df['eco_growth_rate'] = df['total_eco'].pct_change() * 100  
        df['ice_growth_rate'] = df['total_ice'].pct_change() * 100  
         
        fig_trend.add_trace(  
            go.Scatter(x=df['year'][1:], y=df['eco_growth_rate'][1:], mode='lines+markers',  
                      name='친환경 성장률', line_color='blue'),  
            row=1, col=2  
        )  
        fig_trend.add_trace(  
            go.Scatter(x=df['year'][1:], y=df['ice_growth_rate'][1:], mode='lines+markers',  
                      name='내연기관 성장률', line_color='orange'),  
            row=1, col=2  
        )  
         
        fig_trend.update_layout(height=500, title_text="변화 트렌드 분석", title_font_size=18)  
        fig_trend.update_xaxes(tickangle=45)  
         
        st.plotly_chart(fig_trend, use_container_width=True)  
         
        # 4. 데이터베이스 뷰어  
        st.subheader("📊 데이터베이스 뷰어")  
         
        # 조회 옵션 선택 (3개 박스)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            view_type = st.selectbox("조회 방식", ["전체", "연도별", "월별"])
        
        with col2:
            if view_type == "전체":
                st.selectbox("기간 선택", ["전체 기간"], disabled=True)
                selected_periods = ["전체"]
            elif view_type == "연도별":
                year_options = [str(year) for year in range(2015, 2025)]
                
                # 선택된 연도 개수 표시
                if 'selected_periods' not in st.session_state or st.session_state.get('last_period_type') != 'year':
                    st.session_state.selected_periods = ["2022", "2024"]
                    st.session_state.last_period_type = 'year'
                
                selected_count = len(st.session_state.selected_periods)
                
                with st.expander(f"📅 연도 선택 ({selected_count}개 선택됨)", expanded=False):
                    # 전체 선택 체크박스
                    select_all_years = st.checkbox("📋 전체 연도 선택", key="all_years")
                    
                    if select_all_years:
                        st.session_state.selected_periods = st.multiselect(
                            "연도를 선택하세요:",
                            year_options,
                            default=year_options,
                            key="years_multi"
                        )
                    else:
                        st.session_state.selected_periods = st.multiselect(
                            "연도를 선택하세요:",
                            year_options,
                            default=st.session_state.selected_periods,
                            key="years_multi"
                        )
                    
                    # 빠른 선택 버튼들
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("📈 최근 3년", key="recent_3_years"):
                            st.session_state.selected_periods = ["2022", "2023", "2024"]
                            st.rerun()
                    with col_b:
                        if st.button("📊 비교년도", key="compare_years"):
                            st.session_state.selected_periods = ["2015", "2020", "2024"]
                            st.rerun()
                    with col_c:
                        if st.button("🔄 초기화", key="reset_years"):
                            st.session_state.selected_periods = ["2022", "2024"]
                            st.rerun()
                
                selected_periods = st.session_state.selected_periods
                
            else:  # 월별
                month_options = []
                for year in range(2015, 2025):
                    for month in range(1, 13):
                        month_options.append(f"{year}-{month:02d}")
                
                # 선택된 연월 개수 표시
                if 'selected_periods' not in st.session_state or st.session_state.get('last_period_type') != 'month':
                    st.session_state.selected_periods = ["2024-01", "2024-12"]
                    st.session_state.last_period_type = 'month'
                
                selected_count = len(st.session_state.selected_periods)
                
                with st.expander(f"📅 연월 선택 ({selected_count}개 선택됨)", expanded=False):
                    # 전체 선택 체크박스
                    select_all_months = st.checkbox("📋 전체 연월 선택", key="all_months")
                    
                    if select_all_months:
                        st.session_state.selected_periods = st.multiselect(
                            "연월을 선택하세요:",
                            month_options,
                            default=month_options,
                            key="months_multi"
                        )
                    else:
                        st.session_state.selected_periods = st.multiselect(
                            "연월을 선택하세요:",
                            month_options,
                            default=st.session_state.selected_periods,
                            key="months_multi"
                        )
                    
                    # 빠른 선택 버튼들
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("📈 2024년", key="year_2024"):
                            st.session_state.selected_periods = [f"2024-{month:02d}" for month in range(1, 13)]
                            st.rerun()
                    with col_b:
                        if st.button("📊 분기별", key="quarterly"):
                            st.session_state.selected_periods = ["2024-03", "2024-06", "2024-09", "2024-12"]
                            st.rerun()
                    with col_c:
                        if st.button("🔄 초기화", key="reset_months"):
                            st.session_state.selected_periods = ["2024-01", "2024-12"]
                            st.rerun()
                
                selected_periods = st.session_state.selected_periods
        
        with col3:
            # 엔진 종류 선택 (접기/펼치기 방식)
            engine_options = ["전기차(EV)", "하이브리드(HEV)", "수소차(FCEV)", "CNG", "기타", "가솔린", "디젤", "LPG"]
            
            if view_type == "전체":
                default_engines = engine_options
            else:
                default_engines = ["전기차(EV)", "가솔린"]
            
            # 선택된 엔진 개수 표시
            if 'selected_engines' not in st.session_state or st.session_state.get('last_view_type') != view_type:
                st.session_state.selected_engines = default_engines
                st.session_state.last_view_type = view_type
            
            selected_count = len(st.session_state.selected_engines)
            
            with st.expander(f"🔧 엔진 종류 선택 ({selected_count}개 선택됨)", expanded=False):
                # 전체 선택 체크박스
                select_all_engines = st.checkbox("📋 전체 엔진 선택", key="all_engines")
                
                if select_all_engines:
                    st.session_state.selected_engines = st.multiselect(
                        "엔진 종류를 선택하세요:",
                        engine_options,
                        default=engine_options,
                        key=f"engines_{view_type}"
                    )
                else:
                    st.session_state.selected_engines = st.multiselect(
                        "엔진 종류를 선택하세요:",
                        engine_options,
                        default=st.session_state.selected_engines,
                        key=f"engines_{view_type}"
                    )
                
                # 빠른 선택 버튼들
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("🌱 친환경만", key=f"eco_only_{view_type}"):
                        st.session_state.selected_engines = ["전기차(EV)", "하이브리드(HEV)", "수소차(FCEV)", "CNG", "기타"]
                        st.rerun()
                with col_b:
                    if st.button("⛽ 내연기관만", key=f"ice_only_{view_type}"):
                        st.session_state.selected_engines = ["가솔린", "디젤", "LPG"]
                        st.rerun()
                with col_c:
                    if st.button("🔄 초기화", key=f"reset_{view_type}"):
                        st.session_state.selected_engines = default_engines
                        st.rerun()
            
            selected_engines = st.session_state.selected_engines
        
        if selected_engines and selected_periods:
            # 선택된 옵션에 따라 데이터 조회
            connection = get_db_connection()
            if connection:
                try:
                    if view_type == "전체":
                        # 전체 기간 총합 데이터 조회
                        query = """
                        SELECT 
                            '전체' as '구분',
                            SUM(e.ev) as '전기차(EV)',
                            SUM(e.hev) as '하이브리드(HEV)', 
                            SUM(e.fcev) as '수소차(FCEV)',
                            SUM(e.cng) as 'CNG',
                            SUM(e.etc) as '기타',
                            SUM(i.gasoline) as '가솔린',
                            SUM(i.diesel) as '디젤',
                            SUM(i.lpg) as 'LPG'
                        FROM dim_monthly d
                        JOIN eco_monthly e ON d.date_key = e.date_key
                        JOIN ice_monthly i ON d.date_key = i.date_key
                        WHERE d.year BETWEEN 2015 AND 2024
                        """
                        
                    elif view_type == "연도별":
                        # 선택된 연도들의 데이터 조회
                        years_str = "','".join(selected_periods)
                        query = f"""
                        SELECT 
                            d.year as '구분',
                            SUM(e.ev) as '전기차(EV)',
                            SUM(e.hev) as '하이브리드(HEV)', 
                            SUM(e.fcev) as '수소차(FCEV)',
                            SUM(e.cng) as 'CNG',
                            SUM(e.etc) as '기타',
                            SUM(i.gasoline) as '가솔린',
                            SUM(i.diesel) as '디젤',
                            SUM(i.lpg) as 'LPG'
                        FROM dim_monthly d
                        JOIN eco_monthly e ON d.date_key = e.date_key
                        JOIN ice_monthly i ON d.date_key = i.date_key
                        WHERE d.year IN ('{years_str}')
                        GROUP BY d.year
                        ORDER BY d.year DESC
                        """
                        
                    else:  # 월별
                        # 선택된 연월들의 데이터 조회
                        where_conditions = []
                        for period in selected_periods:
                            year, month = period.split('-')
                            where_conditions.append(f"(d.year = {year} AND d.month = {month})")
                        
                        where_clause = " OR ".join(where_conditions)
                        
                        query = f"""
                        SELECT 
                            CONCAT(d.year, '-', LPAD(d.month, 2, '0')) as '구분',
                            e.ev as '전기차(EV)',
                            e.hev as '하이브리드(HEV)', 
                            e.fcev as '수소차(FCEV)',
                            e.cng as 'CNG',
                            e.etc as '기타',
                            i.gasoline as '가솔린',
                            i.diesel as '디젤',
                            i.lpg as 'LPG'
                        FROM dim_monthly d
                        JOIN eco_monthly e ON d.date_key = e.date_key
                        JOIN ice_monthly i ON d.date_key = i.date_key
                        WHERE {where_clause}
                        ORDER BY d.year DESC, d.month DESC
                        """
                    
                    db_df = pd.read_sql(query, connection)
                    
                    # 선택된 엔진 종류만 표시
                    columns_to_show = ['구분'] + selected_engines
                    display_db_df = db_df[columns_to_show].copy()
                    
                    # 숫자 포맷팅
                    for col in selected_engines:
                        if col in display_db_df.columns:
                            display_db_df[col] = display_db_df[col].apply(lambda x: f"{x:,}")
                    
                    st.dataframe(display_db_df, use_container_width=True, height=400)
                    
                    # 데이터 다운로드 버튼
                    csv = display_db_df.to_csv(index=False)
                    st.download_button(
                        label="📥 CSV로 다운로드",
                        data=csv,
                        file_name=f"차량등록_{view_type}_{len(selected_engines)}종류.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"데이터 조회 실패: {e}")
                finally:
                    connection.close()
        else:
            if not selected_engines:
                st.info("👆 엔진 종류를 하나 이상 선택해주세요.")
            if not selected_periods and view_type != "전체":
                st.info("👆 조회할 기간을 선택해주세요.")
         
        # 5. 인사이트 (고급 분석 결과)  
        st.markdown(f"""  
        <div class="feature-card">  
            <h3 style="color: #2a5298;">📌 주요 분석 시사점</h3>  
            <ul>  
                <li><strong>지속적 성장세:</strong> 지난 10년간 친환경차 등록은 연평균 약 18% 증가하며 뚜렷한 확대 추세를 보임</li>  
                <li><strong>기술 주도권:</strong> 전기차가 친환경차 전체의 약 55%를 차지하며 시장 성장을 주도</li>  
                <li><strong>정책 효과:</strong> 2020년 이후 그린뉴딜 및 보조금 정책으로 성장 속도가 가속화됨</li>  
                <li><strong>향후 전망:</strong> 현재 추세 지속 시 2030년에는 전체 등록 차량의 약 80%가 친환경차일 것으로 예측됨</li>  
            </ul>  
        </div>  
        """, unsafe_allow_html=True)  
         
    else:  
        st.error("고급 분석을 위한 데이터를 불러올 수 없습니다. 데이터베이스 연결을 확인해주세요.")  
         
        # 샘플 데이터로 대체  
        st.info("샘플 데이터로 차트 기능을 시연합니다.")  
         
        sample_df = pd.DataFrame({  
            'year': range(2015, 2025),  
            'total_eco': [43105, 62161, 84201, 109415, 142563, 186763, 244820, 336675, 458902, 621378],  
            'total_ice': [2978583, 2871230, 2759836, 2644874, 2528544, 2408726, 2285530, 2159168, 2030615, 1901341]  
        })  
         
        sample_df['total_cars'] = sample_df['total_eco'] + sample_df['total_ice']  
        sample_df['eco_ratio'] = (sample_df['total_eco'] / sample_df['total_cars'] * 100).round(1)  
         
        fig_sample = px.line(sample_df, x='year', y='eco_ratio',  
                           title='샘플 데이터: 친환경차량 비율 추이',  
                           markers=True)  
        st.plotly_chart(fig_sample, use_container_width=True)