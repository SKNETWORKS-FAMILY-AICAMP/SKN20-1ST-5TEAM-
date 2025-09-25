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
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")
        return None

# 브랜드 자동 추출 함수
@st.cache_data(ttl=300)  # 5분 캐시
def get_dynamic_brands():
    """DB에서 브랜드를 자동으로 추출"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        query = "SELECT DISTINCT company FROM faq ORDER BY company"
        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        
        # 브랜드 목록 생성
        brands = [row[0] for row in results]
        
        # 브랜드명 매핑 (표시용)
        brand_display_names = []
        for brand in brands:
            if brand == 'hyundai':
                brand_display_names.append('현대')
            elif brand == 'genesis':
                brand_display_names.append('제네시스')
            else:
                # 새로운 브랜드가 추가되어도 자동 처리
                brand_display_names.append(brand.title())
        
        return brands, brand_display_names
        
    except Exception as e:
        st.error(f"브랜드 추출 실패: {e}")
        if connection:
            connection.close()
        return [], []

# 브랜드별 카테고리 자동 추출 함수
@st.cache_data(ttl=300)  # 5분 캐시
def get_dynamic_categories():
    """DB에서 브랜드별 카테고리를 자동으로 추출"""
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor()
        query = "SELECT company, question FROM faq"
        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        
        # 브랜드별 카테고리 추출
        categories_by_brand = {}
        
        for company_name, question in results:
            if company_name not in categories_by_brand:
                categories_by_brand[company_name] = set()
            
            # 브랜드별 패턴에 따라 카테고리 추출
            category = extract_category_from_question_text(question, company_name)
            if category and category.strip():
                categories_by_brand[company_name].add(category)
        
        # set을 sorted list로 변환
        for brand in categories_by_brand:
            categories_by_brand[brand] = sorted(list(categories_by_brand[brand]))
        
        return categories_by_brand
        
    except Exception as e:
        st.error(f"카테고리 추출 실패: {e}")
        if connection:
            connection.close()
        return {}

def extract_category_from_question_text(question, company):
    """질문 텍스트에서 카테고리를 자동으로 추출 (완전 자동화)"""
    
    if company == 'hyundai':
        # 현대 패턴: [ 카테고리 > 세부카테고리 ] 또는 [ 카테고리 ]
        main_category_match = re.search(r'^\[\s*([^\>\]]+)', question)
        if main_category_match:
            category = main_category_match.group(1).strip()
            return category
    
    elif company == 'genesis':
        # 제네시스 패턴: [카테고리]
        category_match = re.search(r'^\[([^\]]+)\]', question)
        if category_match:
            category = category_match.group(1).strip()
            return category
    
    else:
        # 새로운 브랜드에 대한 일반적인 패턴 (대괄호 감지)
        category_match = re.search(r'^\[([^\]]+)\]', question)
        if category_match:
            category = category_match.group(1).strip()
            return category
    
    return None

# 브랜드별 질문 정리 함수
def clean_question_title(question, company):
    """브랜드별 질문에서 카테고리 부분 제거하고 깨끗한 질문만 추출"""
    
    if company == 'hyundai':
        # 현대: 모든 대괄호 제거
        clean_question = re.sub(r'\[.*?\]', '', question).strip()
        return clean_question
    
    elif company == 'genesis':
        # 제네시스: 첫 번째 대괄호만 제거
        clean_question = re.sub(r'^\[.*?\]\s*', '', question).strip()
        return clean_question
    
    else:
        # 새로운 브랜드에 대한 일반적인 처리
        clean_question = re.sub(r'^\[.*?\]\s*', '', question).strip()
        return clean_question
    
    return question

# FAQ 데이터 가져오기 함수 (완전 자동화)
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
        
        # 카테고리 필터 (완전 자동화 - 하드코딩 없음)
        if category and category != 'all':
            # 대괄호 안에 해당 카테고리가 포함된 질문 검색
            query += " AND question REGEXP %s"
            # 정규식으로 [카테고리] 또는 [카테고리 > ...] 패턴 매칭
            params.append(f'^\\[.*{re.escape(category)}.*\\]')
        
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

# 브랜드 표시명을 실제 DB값으로 변환
def get_brand_db_value(display_name, brands, brand_display_names):
    """표시명을 DB의 실제 브랜드명으로 변환"""
    if display_name == '전체':
        return 'all'
    
    try:
        index = brand_display_names.index(display_name)
        return brands[index]
    except (ValueError, IndexError):
        return display_name.lower()

def show_faq():
    """FAQ 페이지를 표시하는 메인 함수"""
    
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">❓ 자주 묻는 질문</h1>
        <p class="hero-subtitle">자동 감지된 브랜드의 차량 관련 궁금한 점들을 확인해보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 동적 브랜드 및 카테고리 로딩
    with st.spinner("브랜드와 카테고리를 자동으로 감지하는 중..."):
        brands, brand_display_names = get_dynamic_brands()
        all_categories = get_dynamic_categories()
    
    # 검색 및 필터 섹션
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        # 동적 브랜드 선택 (완전 자동화)
        brand_options = ["전체"] + brand_display_names
        selected_brand_display = st.selectbox(
            "🏢 브랜드", 
            brand_options,
            help="DB에서 자동 감지된 브랜드를 선택하세요"
        )
    
    with col2:
        # 선택된 브랜드의 실제 DB값 가져오기
        selected_brand_db = get_brand_db_value(selected_brand_display, brands, brand_display_names)
        
        # 브랜드별 동적 카테고리 옵션 (완전 자동화)
        if selected_brand_display != "전체" and selected_brand_db in all_categories:
            category_options = ["전체"] + all_categories[selected_brand_db]
        elif selected_brand_display == "전체":
            # 모든 브랜드의 카테고리 합치기
            all_cats = set()
            for brand_cats in all_categories.values():
                all_cats.update(brand_cats)
            category_options = ["전체"] + sorted(list(all_cats))
        else:
            category_options = ["전체"]
        
        selected_category = st.selectbox(
            "📂 카테고리", 
            category_options,
            help="자동 감지된 카테고리를 선택하세요"
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
            <p><strong>🤖 완전 자동화:</strong> 브랜드와 카테고리 모두 데이터베이스에서 자동으로 감지됩니다.</p>
            <p><strong>🏢 동적 브랜드:</strong> 새로운 브랜드가 DB에 추가되면 자동으로 선택 옵션에 나타납니다.</p>
            <p><strong>📂 동적 카테고리:</strong> 브랜드별로 실시간 감지된 카테고리가 표시됩니다.</p>
            <p><strong>🔍 키워드 검색:</strong> 궁금한 내용의 키워드를 입력하여 관련 FAQ를 빠르게 찾으세요.</p>
            <p><strong>💬 FAQ 확장:</strong> 질문을 클릭하면 상세한 답변을 확인할 수 있습니다.</p>
            <p><strong>🔄 무한 확장:</strong> 크롤링으로 새 데이터 추가 시 모든 것이 자동 갱신됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 카테고리도 완전 자동화 (하드코딩 제거)
    category_filter = selected_category if selected_category != "전체" else "all"
    
    # 필터 변경 감지 및 페이지 리셋
    current_filters = f"{selected_brand_db}_{category_filter}_{search_keyword.strip()}"
    if 'prev_filters' not in st.session_state:
        st.session_state.prev_filters = current_filters
    
    if st.session_state.prev_filters != current_filters:
        st.session_state.current_page = 1  # 페이지 리셋
        st.session_state.prev_filters = current_filters
    
    # FAQ 데이터 로딩
    with st.spinner("FAQ 데이터를 불러오는 중..."):
        faq_data = get_faq_data(
            company=selected_brand_db,
            category=category_filter,
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
        
        # 페이지네이션 구현 (10개 고정)
        items_per_page = 10
        total_pages = (len(faq_data) + items_per_page - 1) // items_per_page
        
        # 현재 페이지 상태 초기화
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
            
        # 페이지 범위 벗어남 방지
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = total_pages
        
        current_page = st.session_state.current_page
        
        # 현재 페이지에 해당하는 데이터만 추출
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_faq_data = faq_data[start_idx:end_idx]
        
        # FAQ 목록을 카드 형태로 표시 (페이지별)
        for faq in page_faq_data:
            idfaq, company, question, answer = faq
            
            # 자동 카테고리 추출 (표시용)
            category_badge = extract_category_from_question_text(question, company)
            if not category_badge:
                category_badge = "기타"
            
            # 브랜드별 질문 제목 정리
            clean_question = clean_question_title(question, company)
            
            # 브랜드 배지 색상 (동적 처리)
            if company == "hyundai":
                brand_color = "#00AAD2"
                brand_name = "현대"
            elif company == "genesis":
                brand_color = "#2F1B14"
                brand_name = "제네시스"
            else:
                # 새로운 브랜드에 대한 기본 색상
                brand_color = "#6c757d"
                brand_name = company.title()
            
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
        
        # 페이지네이션 (FAQ 카드들 아래쪽에 배치)
        if total_pages > 1:
            st.markdown("---")  # 구분선
            
            # 페이지 범위 계산 (현재 페이지 ±2, 총 5개)
            start_page = max(1, current_page - 2)
            end_page = min(total_pages, current_page + 2)
            
            # 5개 미만이면 범위 조정
            if end_page - start_page < 4:
                if start_page == 1:
                    end_page = min(total_pages, start_page + 4)
                else:
                    start_page = max(1, end_page - 4)
            
            # 중앙 정렬을 위한 컨테이너
            col_left, col_center, col_right = st.columns([1, 2, 1])
            
            with col_center:
                # 페이지 버튼 생성 (간단한 스타일)
                page_range = list(range(start_page, end_page + 1))
                cols = st.columns(len(page_range))
                
                for i, page_num in enumerate(page_range):
                    with cols[i]:
                        if page_num == current_page:
                            # 현재 페이지 (간단한 강조)
                            st.markdown(f"**[{page_num}]**")
                        else:
                            # 다른 페이지 (클릭 가능한 버튼)
                            if st.button(f"{page_num}", key=f"page_btn_{page_num}"):
                                st.session_state.current_page = page_num
                                st.rerun()
    
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