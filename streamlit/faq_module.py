import streamlit as st
import pymysql
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

# FAQ 데이터 가져오기 함수
def get_faq_data():
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # FAQ 테이블에서 모든 데이터 가져오기
        query = """
        SELECT idfaq, company, question, answer
        FROM faq
        ORDER BY company, idfaq
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        connection.close()
        return results
        
    except Exception as e:
        st.error(f"FAQ 데이터 조회 실패: {e}")
        connection.close()
        return None

def show_faq():
    """FAQ 페이지를 표시하는 메인 함수"""
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">❓ 자주 묻는 질문</h1>
        <p class="hero-subtitle">프로젝트 관련 궁금한 점들을 확인해보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 드롭다운 구성
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_brand = st.selectbox("🏢 대분류 (브랜드)", ["선택하세요", "현대", "기아"])
    
    with col2:
        if selected_brand != "선택하세요":
            categories = ["전기차", "하이브리드", "일반차량"]
            selected_category = st.selectbox("📂 소분류 (차종)", ["선택하세요"] + categories)
        else:
            selected_category = st.selectbox("📂 소분류 (차종)", ["선택하세요"])
    
    with col3:
        if selected_brand != "선택하세요" and selected_category != "선택하세요":
            selected_question = st.selectbox("❓ FAQ 선택", ["선택하세요", "질문 1", "질문 2", "질문 3"])
        else:
            selected_question = st.selectbox("❓ FAQ 선택", ["선택하세요"])
    
    # FAQ 데이터 로딩 및 표시
    if (selected_brand != "선택하세요" and selected_category != "선택하세요" and selected_question != "선택하세요"):
        
        # 데이터베이스에서 FAQ 데이터 가져오기
        with st.spinner("FAQ 데이터를 불러오는 중..."):
            faq_data = get_faq_data()
        
        if faq_data:
            # 선택된 브랜드와 카테고리에 맞는 FAQ 찾기 (임시로 첫 번째 데이터 표시)
            # 실제로는 선택된 조건에 맞는 데이터를 필터링해야 함
            
            st.markdown(f"""
            <div class="answer-box">
                <h4 style="color: #2a5298;">💬 {selected_brand} - {selected_category} - {selected_question}</h4>
                <p><strong>질문:</strong> 이것은 {selected_brand}의 {selected_category} 관련 {selected_question}입니다.</p>
                <p><strong>답변:</strong> 현재 데이터베이스에서 FAQ 데이터를 가져오는 기능이 구현되었습니다. 
                실제 운영시에는 선택하신 브랜드와 차종에 맞는 구체적인 질문과 답변이 표시됩니다.</p>
                <p style="color: #666; font-style: italic; margin-top: 1rem;">
                📝 참고: 데이터베이스에서 {len(faq_data)}개의 FAQ 항목을 확인했습니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 데이터베이스 연결 실패시 기본 답변
            st.markdown(f"""
            <div class="answer-box">
                <h4 style="color: #2a5298;">💬 {selected_brand} - {selected_category} - {selected_question}</h4>
                <p><strong>질문:</strong> 이것은 {selected_brand}의 {selected_category} 관련 {selected_question}입니다.</p>
                <p><strong>답변:</strong> 현재 데이터베이스에 연결할 수 없어 기본 답변을 표시합니다. 
                실제 운영시에는 MySQL 데이터베이스에서 FAQ 내용을 가져와서 표시할 예정입니다.</p>
                <p style="color: #666; font-style: italic; margin-top: 1rem;">
                ⚠️ 데이터베이스 연결을 확인해주세요.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif selected_brand != "선택하세요":
        st.info("💡 소분류와 FAQ를 선택해주세요.")
    else:
        st.info("💡 브랜드를 먼저 선택해주세요.")
    
    # 사용 안내
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: #2a5298;">📖 FAQ 사용 안내</h4>
        <p><strong>1단계:</strong> 브랜드(현대/기아)를 선택하세요.</p>
        <p><strong>2단계:</strong> 차량 분류(전기차/하이브리드/일반차량)를 선택하세요.</p>
        <p><strong>3단계:</strong> 궁금한 질문을 선택하면 답변이 표시됩니다.</p>
        <p style="color: #666; font-style: italic;">📝 참고: FAQ 내용은 MySQL 데이터베이스와 연동하여 실시간으로 업데이트됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 추가 정보 섹션
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: #2a5298;">🔧 기술 구현 정보</h4>
        <p><strong>데이터베이스:</strong> MySQL의 'faq' 테이블과 연동</p>
        <p><strong>테이블 구조:</strong> idfaq, company, question, answer 컬럼</p>
        <p><strong>기능:</strong> 브랜드별, 카테고리별 FAQ 분류 및 표시</p>
        <p><strong>확장 계획:</strong> 검색 기능, FAQ 추가/수정 관리자 기능</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 자주 묻는 질문 예시 (임시 데이터)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📋 FAQ 예시 (임시 데이터)")
    
    # 임시 FAQ 데이터를 테이블로 표시
    example_faq = [
        {"브랜드": "현대", "차종": "전기차", "질문": "아이오닉의 충전시간은?", "상태": "DB 연동 예정"},
        {"브랜드": "현대", "차종": "하이브리드", "질문": "연비는 얼마나 되나요?", "상태": "DB 연동 예정"},
        {"브랜드": "기아", "차종": "전기차", "질문": "EV6의 주행거리는?", "상태": "DB 연동 예정"},
        {"브랜드": "기아", "차종": "하이브리드", "질문": "니로의 가격대는?", "상태": "DB 연동 예정"}
    ]
    
    st.dataframe(example_faq, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)