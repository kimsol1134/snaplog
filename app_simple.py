#!/usr/bin/env python3
"""
SnapLog - 자연스러운 일상 기록 생성기 (심플 버전)
Streamlit 기본 테마를 사용하는 깔끔한 버전

Author: Claude Code
Version: 2.1 (Simple)
"""

import streamlit as st
import os
import json
import tempfile
import time
import base64
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path

# 외부 모듈 import
from snaplog_natural import (
    generate_natural_diary,
    extract_image_metadata,
    extract_practical_info
)

# ================================================================================
# 설정 및 상수
# ================================================================================

PAGE_CONFIG = {
    "page_title": "SnapLog - 자연스러운 일상 기록",
    "page_icon": "🌅",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

STYLE_OPTIONS = {
    "자연스럽고 편안한": "자연스러운",
    "감성적이고 서정적인": "감성적", 
    "간결하고 명확한": "간결한",
    "상세하고 구체적인": "상세한"
}

SUPPORTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']
MAX_IMAGES = 10
DIARY_STORAGE_DIR = "diaries"

# ================================================================================
# 최소한의 CSS 스타일링
# ================================================================================

def load_minimal_css():
    """최소한의 CSS 스타일링만 적용"""
    st.markdown("""
    <style>
    /* 설정 헤더 숨기기 */
    .stSidebar h2:first-of-type,
    section[data-testid="stSidebar"] h2:first-of-type {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ================================================================================
# 유틸리티 함수들
# ================================================================================

def init_diary_storage() -> Path:
    """일기 저장 폴더 초기화"""
    diary_dir = Path(DIARY_STORAGE_DIR)
    diary_dir.mkdir(exist_ok=True)
    return diary_dir

def get_image_base64(uploaded_file) -> str:
    """업로드된 파일을 base64로 변환"""
    return base64.b64encode(uploaded_file.getvalue()).decode()

# ================================================================================
# 일기 관리 함수들
# ================================================================================

def save_diary(diary_content: str, diary_date: date, style: str, image_count: int) -> Path:
    """일기를 JSON 형태로 저장"""
    diary_dir = init_diary_storage()
    
    # 파일명: YYYY-MM-DD.json
    filename = f"{diary_date.strftime('%Y-%m-%d')}.json"
    filepath = diary_dir / filename
    
    # 기존 파일이 있으면 읽어오기
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
    
    # 새로운 일기 추가 (시간을 키로 사용)
    timestamp = datetime.now().strftime('%H:%M:%S')
    data[timestamp] = {
        "content": diary_content,
        "style": style,
        "image_count": image_count,
        "created_at": datetime.now().isoformat()
    }
    
    # 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_saved_diaries() -> Dict[str, Dict]:
    """저장된 일기 목록 불러오기"""
    diary_dir = init_diary_storage()
    diary_files = list(diary_dir.glob("*.json"))
    diary_files.sort(reverse=True)  # 최신순 정렬
    
    diaries = {}
    for file in diary_files:
        date_str = file.stem
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                diaries[date_str] = data
        except Exception as e:
            st.error(f"일기 파일 읽기 오류 ({file.name}): {e}")
    
    return diaries

# ================================================================================
# UI 컴포넌트 함수들
# ================================================================================

def display_saved_diary(diary_data: Dict, selected_time: str = None):
    """저장된 일기 표시"""
    if selected_time and selected_time in diary_data:
        entry = diary_data[selected_time]
        st.subheader(f"🕐 {selected_time}")
        st.info(f"스타일: {entry['style']} | 사진: {entry['image_count']}장")
        st.text_area("일기 내용", entry['content'], height=300, disabled=True)
    else:
        for time_key, entry in diary_data.items():
            with st.expander(f"🕐 {time_key} - {entry['style']} 스타일"):
                st.info(f"사진: {entry['image_count']}장 | 생성일: {entry['created_at'][:19]}")
                st.write(entry['content'])

def display_api_status():
    """API 키 상태 표시"""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ Google API Key: 미설정")
        st.info("💡 .env 파일에 GOOGLE_API_KEY를 설정해주세요.")

def display_usage_instructions():
    """사용 방법 안내 표시"""
    st.info("""
    🎯 **사용 방법**
    
    1. 왼쪽 사이드바에서 **사진을 업로드**하세요
    2. **일기 스타일**을 선택하세요
    3. **저장 날짜**를 설정하세요
    4. 아래 **'일기 생성하기'** 버튼을 클릭하세요
    """)

def display_detailed_instructions():
    """자세한 사용법 표시"""
    with st.expander("📖 자세한 사용법"):
        st.markdown("""
        ### 📸 사진 업로드
        - JPEG, PNG 형식 지원
        - 최대 10장까지 업로드 가능
        - 사진에 시간/위치 정보가 있으면 더 정확한 일기 생성
        
        ### ✨ 스타일 선택
        - **자연스러운**: 친구에게 말하듯 편안한 톤
        - **감성적**: 서정적이고 감성적인 표현
        - **간결한**: 핵심만 담은 명확한 기록
        - **상세한**: 구체적이고 자세한 서술
        
        ### 💾 저장 기능
        - 날짜별로 일기 저장
        - 같은 날짜에 여러 일기 저장 가능
        - 사이드바에서 과거 일기 조회
        """)

# ================================================================================
# 메인 애플리케이션
# ================================================================================

def setup_page():
    """페이지 초기 설정"""
    st.set_page_config(**PAGE_CONFIG)
    load_minimal_css()

def render_header():
    """헤더 렌더링"""
    st.title("🌅 SnapLog - 자연스러운 일상 기록")
    st.markdown('*"사진 속 순간들을 아름다운 일기로 만들어보세요"* ✨')
    st.markdown("---")

def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        # API 키 상태 확인
        display_api_status()
        st.markdown("---")
        
        # 파일 업로드
        st.subheader("📷 사진 업로드")
        uploaded_files = st.file_uploader(
            "사진 선택 (최대 10장)",
            type=SUPPORTED_IMAGE_TYPES,
            accept_multiple_files=True,
            help="JPEG, PNG 형식의 사진을 최대 10장까지 업로드",
            key="photo_uploader"
        )
        
        # 파일 수 제한 확인
        if uploaded_files and len(uploaded_files) > MAX_IMAGES:
            st.error(f"⚠️ 최대 {MAX_IMAGES}장까지만 업로드 가능합니다.")
            uploaded_files = uploaded_files[:MAX_IMAGES]
        
        if uploaded_files:
            st.success(f"📸 {len(uploaded_files)}장 업로드됨")
        
        # 스타일 선택
        st.subheader("🖋️ 일기 스타일")
        selected_style_desc = st.selectbox(
            "스타일 선택",
            options=list(STYLE_OPTIONS.keys()),
            index=0,
            key="style_selector"
        )
        selected_style = STYLE_OPTIONS[selected_style_desc]
        
        # 날짜 선택
        st.subheader("📅 저장 날짜")
        diary_date = st.date_input(
            "날짜 선택",
            value=date.today(),
            help="일기를 저장할 날짜를 선택하세요.",
            key="date_selector"
        )
        
        st.markdown("---")
        
        # 저장된 일기 보기
        st.header("📚 저장된 일기")
        saved_diaries = load_saved_diaries()
        
        selected_date = None
        selected_time = None
        
        if saved_diaries:
            selected_date = st.selectbox(
                "날짜 선택",
                options=list(saved_diaries.keys()),
                format_func=lambda x: x,
                key="saved_date_selector"
            )
            
            if selected_date:
                diary_data = saved_diaries[selected_date]
                if len(diary_data) > 1:
                    selected_time = st.selectbox(
                        "시간 선택",
                        options=list(diary_data.keys()),
                        key="saved_time_selector"
                    )
                else:
                    selected_time = list(diary_data.keys())[0]
        else:
            st.info("저장된 일기가 없습니다.")
    
    return uploaded_files, selected_style_desc, selected_style, diary_date, saved_diaries, selected_date, selected_time

def render_main_content(uploaded_files, selected_style_desc, selected_style, diary_date, saved_diaries, selected_date, selected_time):
    """메인 컨텐츠 렌더링"""
    if not uploaded_files:
        display_usage_instructions()
        display_detailed_instructions()
    else:
        # 업로드된 이미지 미리보기
        st.subheader(f"📷 업로드된 사진 ({len(uploaded_files)}장)")
        st.markdown('*"소중한 순간들을 담은 사진들이네요"* 🌸')
        
        # 기본 이미지 그리드 표시
        cols = st.columns(min(len(uploaded_files), 3))
        for i, uploaded_file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(uploaded_file, caption=f"사진 {i+1}", use_container_width=True)
        
        st.markdown("---")
        
        # 일기 생성 버튼과 로직
        handle_diary_generation(uploaded_files, selected_style_desc, selected_style, diary_date)
    
    # 저장된 일기 표시 (사이드바에서 선택된 경우)
    if saved_diaries and selected_date:
        st.markdown("---")
        st.subheader(f"📖 저장된 일기 - {selected_date}")
        display_saved_diary(saved_diaries[selected_date], selected_time)

def handle_diary_generation(uploaded_files, selected_style_desc, selected_style, diary_date):
    """일기 생성 로직 처리"""
    # 일기 생성 버튼
    generate_button = st.button(
        "🤖 일기 생성하기", 
        type="primary", 
        use_container_width=True,
        disabled=not os.getenv("GOOGLE_API_KEY")
    )
    
    if generate_button:
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("❌ Google API Key가 설정되지 않았습니다.")
            st.info("💡 .env 파일에 GOOGLE_API_KEY를 설정해주세요.")
            return
        
        # 세션 상태에 일기 내용 저장
        if 'generated_diary' not in st.session_state:
            st.session_state.generated_diary = None
            st.session_state.diary_metadata = None
        
        with st.spinner("🤖 AI가 일기를 생성하고 있습니다..."):
            try:
                # 진행 상태 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 임시 파일로 저장
                temp_paths = []
                status_text.text("📁 이미지 파일 준비 중...")
                progress_bar.progress(20)
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    for i, uploaded_file in enumerate(uploaded_files):
                        temp_path = os.path.join(temp_dir, f"image_{i+1}.{uploaded_file.name.split('.')[-1]}")
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        temp_paths.append(temp_path)
                    
                    # 일기 생성
                    status_text.text("🔍 이미지 분석 중...")
                    progress_bar.progress(50)
                    
                    diary_content = generate_natural_diary(
                        image_paths=temp_paths,
                        style_preference=selected_style_desc
                    )
                    
                    status_text.text("✅ 일기 생성 완료!")
                    progress_bar.progress(100)
                
                # 세션 상태에 저장
                st.session_state.generated_diary = diary_content
                st.session_state.diary_metadata = {
                    'style': selected_style,
                    'style_desc': selected_style_desc,
                    'date': diary_date,
                    'image_count': len(uploaded_files)
                }
                
                # UI 정리
                progress_bar.empty()
                status_text.empty()
                st.success("🎉 일기 생성이 완료되었습니다!")
                
            except Exception as e:
                st.error(f"❌ 일기 생성 중 오류가 발생했습니다: {str(e)}")
                st.info("💡 다시 시도해보시거나, API 키 설정을 확인해주세요.")
                if 'generated_diary' in st.session_state:
                    del st.session_state.generated_diary
                    del st.session_state.diary_metadata
    
    # 생성된 일기 표시
    if 'generated_diary' in st.session_state and st.session_state.generated_diary:
        display_generated_diary()

def display_generated_diary():
    """생성된 일기 표시 및 저장 기능"""
    st.markdown("---")
    st.subheader("📝 생성된 일기")
    
    # 메타데이터 표시
    metadata = st.session_state.diary_metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("스타일", metadata['style_desc'])
    with col2:
        st.metric("사진 수", f"{metadata['image_count']}장")
    with col3:
        st.metric("날짜", metadata['date'].strftime('%Y-%m-%d'))
    
    # 일기 내용 표시 (편집 가능)
    edited_diary = st.text_area(
        "일기 내용 (수정 가능)",
        st.session_state.generated_diary,
        height=300,
        help="생성된 일기 내용입니다. 필요시 수정 후 저장하세요.",
        key="diary_editor"
    )
    
    # 저장 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        save_button = st.button(
            "💾 일기 저장하기", 
            type="secondary",
            use_container_width=True,
            key="save_diary_button"
        )
        
        if save_button:
            try:
                saved_path = save_diary(
                    diary_content=edited_diary,
                    diary_date=metadata['date'],
                    style=metadata['style'],
                    image_count=metadata['image_count']
                )
                st.success("💾 일기가 성공적으로 저장되었습니다!")
                st.info(f"📁 저장 위치: {saved_path}")
                st.balloons()
                
                # 저장 후 세션 상태 초기화
                time.sleep(2)  # 사용자가 성공 메시지를 볼 수 있도록
                del st.session_state.generated_diary
                del st.session_state.diary_metadata
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 저장 중 오류가 발생했습니다: {str(e)}")
                st.info("💡 파일 권한을 확인하거나 다시 시도해주세요.")

def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    setup_page()
    
    # 헤더 렌더링
    render_header()
    
    # 사이드바 렌더링 및 상태 가져오기
    uploaded_files, selected_style_desc, selected_style, diary_date, saved_diaries, selected_date, selected_time = render_sidebar()
    
    # 메인 컨텐츠 렌더링
    render_main_content(uploaded_files, selected_style_desc, selected_style, diary_date, saved_diaries, selected_date, selected_time)

if __name__ == "__main__":
    main()