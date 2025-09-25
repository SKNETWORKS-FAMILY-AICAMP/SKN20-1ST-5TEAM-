# pip install streamlit pymysql python-dotenv pandas numpy plotly matplotlib

import streamlit as st
from dotenv import load_dotenv
import os

# 페이지 모듈 import
from graph_analysis_module import show_graph_analysis
from faq_module import show_faq

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="자동차 데이터 분석 프로젝트",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 간단한 CSS 스타일
st.markdown("""
<style>
.main { padding-top: 2rem; }
.hero-section { 
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
    padding: 3rem 2rem; border-radius: 15px; margin-bottom: 2rem; 
    color: white; text-align: center; 
}
.hero-title { font-size: 3rem; font-weight: 700; margin-bottom: 1rem; }
.hero-subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 2rem; }
.feature-card { 
    background: white; padding: 2rem; border-radius: 12px; 
    margin: 1rem 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
    border-left: 4px solid #2a5298; 
}
.metric-card { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    padding: 1.5rem; border-radius: 12px; color: white; 
    text-align: center; margin: 0.5rem 0; 
}
.chart-container { 
    background: white; padding: 2rem; border-radius: 12px; 
    margin: 1rem 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
}
.answer-box { 
    background: #f8f9ff; padding: 1.5rem; border-radius: 8px; 
    border-left: 4px solid #2a5298; margin-top: 1rem; 
}
</style>
""", unsafe_allow_html=True)

# 사이드바
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; color: white; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 2rem;">
    <h2 style="color: white; margin: 0;">🚗 친환경차량 동향</h2>
</div>
""", unsafe_allow_html=True)

# 페이지 선택
if "page" not in st.session_state:
    st.session_state.page = "🏠 메인페이지"

# 버튼 메뉴
if st.sidebar.button("🏠 메인페이지"):
    st.session_state.page = "🏠 메인페이지"

if st.sidebar.button("📊 차량 등록 분석"):
    st.session_state.page = "📊 차량 등록 분석"

if st.sidebar.button("❓ FAQ"):
    st.session_state.page = "❓ FAQ"
    
# 기존 코드와 동일하게 page 변수 사용
page = st.session_state.page


# === 메인페이지 ===
if page == "🏠 메인페이지":
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🚗 서울시 신규등록차량 데이터를 통한 
                <br>친환경차량 동향 분석</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 프로젝트 개요
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2a5298;">📈 데이터 분석</h3>
            <p>최근 10년간 서울시 신규등록차량 데이터를 분석하여 친환경차량과 내연기관차량의 등록 현황을 파악합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2a5298;">🌱 친환경 트렌드</h3>
            <p>전기차, 하이브리드 등 친환경차량의 등록 비율 변화를 시각화하여 미래 자동차 산업의 방향을 제시합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #2a5298;">🎯 시사점</h3>
            <p>데이터 기반의 분석을 통해 자동차 시장의 변화와 정책적 시사점을 도출하고 제시합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 프로젝트 상세
    st.markdown("""
    <div class="feature-card">
        <h2 style="color: #2a5298;">📋 프로젝트 상세</h2>
        <h4 style="color: #2a5298;">🎯 목적</h4>
        <ul>
            <li>서울시 자동차 등록 현황 분석</li>
            <li>친환경차량 도입 현황 파악</li>
            <li>미래 자동차 시장 트렌드 예측</li>
        </ul>
        <h4 style="color: #2a5298;">📊 분석 방법</h4>
        <ul>
            <li>MySQL 데이터베이스 활용</li>
            <li>시계열 데이터 분석</li>
            <li>비율 변화 추이 분석</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# === 그래프 분석 페이지 ===
elif page == "📊 차량 등록 분석":
    show_graph_analysis()

# === FAQ 페이지 ===
elif page == "❓ FAQ":
    show_faq()

# 푸터
st.markdown("---")
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; text-align: center; color: white; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 12px;">
    <h4 style="color: white; margin-bottom: 1rem;">🚗 자동차 데이터 분석 프로젝트</h4>
    <p style="margin: 0;">© 2025.9.25. | Made with 5팀 </p>
</div>
""", unsafe_allow_html=True)