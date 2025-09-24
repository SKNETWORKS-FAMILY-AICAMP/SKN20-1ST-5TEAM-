import streamlit as st
import pymysql
import os
from dotenv import load_dotenv
import re

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
def get_faq_data(company=None, category=None, search_keyword=None):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # 기본 쿼리
        query = """
        SELECT idfaq, company, question, answer
        FROM faq
        WHERE 1=1
        """
        params = []
        
        # 회사 필터
        if company and company.lower() != 'all':
            query += " AND company = %s"
            params.append(company.lower())
        
        # 카테고리 필터 (질문 내용으로 분류)
        if category and category != 'all':
            if category == 'bluelink':
                query += " AND (question LIKE %s OR answer LIKE %s)"
                params.extend(['%블루링크%', '%블루링크%'])
            elif category == 'maintenance':
                query += " AND (question LIKE %s OR question LIKE %s OR question LIKE %s)"
                params.extend(['%정비%', '%에어컨%', '%리모컨%'])
            elif category == 'model_service':
                query += " AND (question LIKE %s OR question LIKE %s)"
                params.extend(['%모델%', '%내비게이션%'])
        
        # 키워드 검색
        if search_keyword:
            query += " AND (question LIKE %s OR answer LIKE %s)"
            params.extend([f'%{search_keyword}%', f'%{search_keyword}%'])
        
        query += " ORDER BY company, idfaq"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        connection.close()
        return results
        
    except Exception as e:
        st.error(f"FAQ 데이터 조회 실패: {e}")
        connection.close()
        return None

# 원본 질문에서 카테고리와 세부 정보 추출하는 함수
def parse_question_structure(question):
    # 예: [ 블루링크 > 가입/해지/변경 ][가입] 블루링크에 가입하려면 어떻게 해야 하나요?
    
    # 첫 번째 대괄호에서 주 카테고리 추출
    main_category_match = re.search(r'^\[\s*([^>\]]+)', question)
    main_category = main_category_match.group(1).strip() if main_category_match else '기타'
    
    # import streamlit as st
import pymysql
import os
from dotenv import load_dotenv
import re
import html

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
def get_faq_data(company=None, category=None, search_keyword=None):
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # 기본 쿼리
        query = """
        SELECT idfaq, company, question, answer
        FROM faq
        WHERE 1=1
        """
        params = []
        
        # 회사 필터
        if company and company.lower() != 'all':
            query += " AND company = %s"
            params.append(company.lower())
        
        # 카테고리 필터 (질문 내용으로 분류)
        if category and category != 'all':
            if category == 'bluelink':
                query += " AND (question LIKE %s OR answer LIKE %s)"
                params.extend(['%블루링크%', '%블루링크%'])
            elif category == 'maintenance':
                query += " AND (question LIKE %s OR question LIKE %s OR question LIKE %s)"
                params.extend(['%정비%', '%에어컨%', '%리모컨%'])
            elif category == 'model_service':
                query += " AND (question LIKE %s OR question LIKE %s)"
                params.extend(['%모델%', '%내비게이션%'])
        
        # 키워드 검색
        if search_keyword:
            query += " AND (question LIKE %s OR answer LIKE %s)"
            params.extend([f'%{search_keyword}%', f'%{search_keyword}%'])
        
        query += " ORDER BY company, idfaq"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        connection.close()
        return results
        
    except Exception as e:
        st.error(f"FAQ 데이터 조회 실패: {e}")
        connection.close()
        return None

# 원본 질문에서 카테고리와 세부 정보 추출하는 함수
def parse_question_structure(question):
    # 예: [ 블루링크 > 가입/해지/변경 ][가입] 블루링크에 가입하려면 어떻게 해야 하나요?
    
    # 첫 번째 대괄호에서 주 카테고리 추출
    main_category_match = re.search(r'^\[\s*([^>\]]+)', question)
    main_category = main_category_match.group(1).strip() if main_category_match else '기타'
    
    # 두 번째 대괄호에서 세부 카테고리 추출
    sub_category_match = re.search(r'\]\[([^\]]+)\]', question)
    sub_category = sub_category_match.group(1).strip() if sub_category_match else ''
    
    # 실제 질문 내용 (대괄호 제거)
    clean_question = re.sub(r'\[.*?\]', '', question).strip()
    
    return {
        'main_category': main_category,
        'sub_category': sub_category,
        'clean_question': clean_question
    }

# FAQ 질문 제목 정리 함수
def clean_question_title(question):
    parsed = parse_question_structure(question)
    return parsed['clean_question']

# 카테고리 추출 함수 (원본 구조 활용)
def extract_category_from_question(question):
    parsed = parse_question_structure(question)
    main_cat = parsed['main_category'].lower()
    
    if '블루링크' in main_cat:
        return '블루링크'
    elif any(keyword in main_cat for keyword in ['차량', '정비', '모델']):
        if '정비' in main_cat:
            return '차량정비' 
        else:
            return '모델서비스'
    else:
        return '기타'

def show_faq():
    """FAQ 페이지를 표시하는 메인 함수"""
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">❓ 자주 묻는 질문</h1>
        <p class="hero-subtitle">현대·기아 차량 관련 궁금한 점들을 확인해보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색 및 필터 섹션
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        selected_brand = st.selectbox(
            "🏢 브랜드", 
            ["전체", "현대", "기아"],
            help="브랜드를 선택하세요"
        )
    
    with col2:
        selected_category = st.selectbox(
            "📂 카테고리", 
            ["전체", "블루링크", "차량정비", "모델서비스"],
            help="FAQ 카테고리를 선택하세요"
        )
    
    with col3:
        search_keyword = st.text_input(
            "🔍 키워드 검색", 
            placeholder="예: 에어컨, 리모컨, 내비게이션...",
            help="질문이나 답변에서 검색할 키워드를 입력하세요"
        )
    
    # 사용 안내 (토글)
    with st.expander("📖 FAQ 사용 안내", expanded=False):
        st.markdown("""
        <div style="padding: 0.5rem;">
            <p><strong>💡 브랜드 선택:</strong> 현대 또는 기아 브랜드를 선택하여 해당 브랜드의 FAQ를 확인하세요.</p>
            <p><strong>📂 카테고리 필터:</strong> 블루링크, 차량정비, 모델서비스 등 원하는 카테고리로 필터링하세요.</p>
            <p><strong>🔍 키워드 검색:</strong> 궁금한 내용의 키워드를 입력하여 관련 FAQ를 빠르게 찾으세요.</p>
            <p><strong>💬 FAQ 확장:</strong> 질문을 클릭하면 상세한 답변을 확인할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 필터 매핑
    brand_map = {"전체": "all", "현대": "hyundai", "기아": "kia"}
    category_map = {"전체": "all", "블루링크": "bluelink", "차량정비": "maintenance", "모델서비스": "model_service"}
    
    # FAQ 데이터 로딩
    with st.spinner("FAQ 데이터를 불러오는 중..."):
        faq_data = get_faq_data(
            company=brand_map[selected_brand],
            category=category_map[selected_category],
            search_keyword=search_keyword.strip() if search_keyword.strip() else None
        )
    
    if faq_data and len(faq_data) > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #e3f2fd 0%, #f8f9fa 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <h4 style="color: #2a5298; margin: 0;">
                📋 검색 결과: {len(faq_data)}개의 FAQ를 찾았습니다
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # FAQ 목록을 카드 형태로 표시
        for faq in faq_data:
            idfaq, company, question, answer = faq
            
            # 카테고리 추출
            category_badge = extract_category_from_question(question)
            
            # 질문 제목 정리
            clean_question = clean_question_title(question)
            
            # 브랜드 배지 색상
            brand_color = "#00AAD2" if company == "hyundai" else "#05141F"
            brand_name = "현대" if company == "hyundai" else "기아"
            
            # FAQ 카드
            with st.expander(f"💬 {clean_question}", expanded=False):
                # 배지 섹션
                col_badge1, col_badge2, col_space = st.columns([1, 1, 3])
                with col_badge1:
                    st.markdown(f"""
                    <span style="background: {brand_color}; color: white; padding: 4px 12px; 
                               border-radius: 15px; font-size: 0.85em; font-weight: bold; 
                               display: inline-block;">
                        {brand_name}
                    </span>
                    """, unsafe_allow_html=True)
                
                with col_badge2:
                    st.markdown(f"""
                    <span style="background: #e3f2fd; color: #1976d2; padding: 4px 12px; 
                               border-radius: 15px; font-size: 0.85em; display: inline-block;">
                        {category_badge}
                    </span>
                    """, unsafe_allow_html=True)
                
                st.markdown("")  # 간격
                
                # 답변 섹션
                st.markdown("**답변:**")
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; 
                           border-left: 4px solid #2a5298; font-family: inherit;">
                    <pre style="background: none; border: none; margin: 0; padding: 0; 
                               font-family: inherit; color: #333; white-space: pre-wrap; 
                               font-size: inherit;">{answer.strip()}</pre>
                </div>
                """, unsafe_allow_html=True)
        
        # 현재 기아 FAQ가 없다는 안내
        if selected_brand == "기아":
            st.markdown("""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; 
                       padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="color: #856404; margin: 0 0 0.5rem 0;">
                    🚧 기아 FAQ 준비 중
                </h4>
                <p style="color: #856404; margin: 0;">
                    기아 브랜드의 FAQ는 현재 준비 중입니다. 빠른 시일 내에 업데이트될 예정입니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    elif faq_data is not None:
        # 검색 결과가 없는 경우
        st.markdown("""
        <div style="background: #f8d7da; border: 1px solid #f5c6cb; 
                   padding: 1.5rem; border-radius: 8px; text-align: center; margin: 2rem 0;">
            <h4 style="color: #721c24; margin: 0 0 0.5rem 0;">
                😔 검색 결과가 없습니다
            </h4>
            <p style="color: #721c24; margin: 0;">
                다른 키워드로 검색하시거나 필터를 변경해보세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # 데이터베이스 연결 실패
        st.error("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요.")