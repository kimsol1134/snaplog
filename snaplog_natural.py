#!/usr/bin/env python3
"""
자연스러운 일상 기록 생성기
- 과도한 감성 표현 제거
- 실용적이고 읽기 좋은 일기 톤
- 실제 있었던 일들 중심의 자연스러운 서술
"""

import os
import base64
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from PIL import Image
from PIL.ExifTags import TAGS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# 환경 변수 로드
load_dotenv()

def get_gemini_model():
    """Google Gemini 2.5 Pro 모델 초기화"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5  # 창의성을 약간 줄여서 더 일관된 톤 유지
    )

def extract_image_metadata(image_path: str) -> Dict[str, Any]:
    """이미지 메타데이터 추출"""
    try:
        with Image.open(image_path) as img:
            metadata = {
                'size': img.size,
                'format': img.format,
                'mode': img.mode
            }
            
            # EXIF 데이터 추출
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[tag] = value
            
            return metadata
    except Exception as e:
        print(f"메타데이터 추출 오류: {e}")
        return {}

def extract_practical_info(metadata: Dict[str, Any]) -> Dict[str, str]:
    """실용적인 시간/장소 정보 추출"""
    info = {
        'time': None,
        'location': None
    }
    
    # 시간 정보 추출
    time_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    for field in time_fields:
        if field in metadata and metadata[field]:
            try:
                time_str = str(metadata[field])
                if ':' in time_str and len(time_str) >= 19:
                    # 2023:12:25 14:30:45 → 2023-12-25 14:30
                    date_part = time_str[:10].replace(':', '-')
                    time_part = time_str[11:16]  # 시:분만 추출
                    info['time'] = f"{date_part} {time_part}"
                    break
            except:
                continue
    
    # GPS 정보 추출 (간단한 위치 힌트로만 사용)
    if 'GPSInfo' in metadata and metadata['GPSInfo']:
        try:
            gps_info = metadata['GPSInfo']
            
            def convert_to_degrees(value):
                if isinstance(value, tuple) and len(value) == 3:
                    d, m, s = value
                    return float(d) + float(m)/60.0 + float(s)/3600.0
                return None
            
            lat = lon = None
            if 2 in gps_info:
                lat = convert_to_degrees(gps_info[2])
                if 1 in gps_info and gps_info[1] == 'S':
                    lat = -lat
            
            if 4 in gps_info:
                lon = convert_to_degrees(gps_info[4])
                if 3 in gps_info and gps_info[3] == 'W':
                    lon = -lon
            
            if lat is not None and lon is not None:
                # 대략적인 위치만 제공 (너무 구체적이지 않게)
                info['location'] = f"위치 정보 있음 (위도: {lat:.2f}, 경도: {lon:.2f})"
        except:
            pass
    
    return info

def encode_image_to_base64(image_path: str) -> str:
    """이미지를 base64로 인코딩"""
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

def generate_natural_diary(image_paths: List[str], style_preference: str = "자연스럽고 편안한") -> str:
    """
    자연스러운 일상 기록 생성
    
    Args:
        image_paths: 분석할 이미지 파일 경로들
        style_preference: 원하는 글쓰기 스타일
        
    Returns:
        str: 생성된 일상 기록
    """
    print(f"자연스러운 일상 기록 생성 시작 - 사진 {len(image_paths)}장")
    
    model = get_gemini_model()
    
    # 각 이미지의 실용적 정보 수집
    practical_hints = []
    image_contents = []
    
    for i, image_path in enumerate(image_paths):
        print(f"사진 {i+1}/{len(image_paths)} 처리 중...")
        
        # 메타데이터에서 실용적 정보 추출
        metadata = extract_image_metadata(image_path)
        info = extract_practical_info(metadata)
        
        hint_parts = []
        if info['time']:
            hint_parts.append(f"촬영시간: {info['time']}")
        if info['location']:
            hint_parts.append(f"위치정보: 있음")
        
        practical_hints.append(f"사진 {i+1}: {' | '.join(hint_parts) if hint_parts else '메타데이터 없음'}")
        
        # 이미지 인코딩
        try:
            img_data = encode_image_to_base64(image_path)
            image_contents.append({
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
            })
        except Exception as e:
            print(f"이미지 인코딩 오류: {e}")
            continue
    
    # 실용적 정보 텍스트 생성
    metadata_text = "\n".join(practical_hints) if practical_hints else "메타데이터 정보 없음"
    
    # 자연스럽고 실용적인 프롬프트 설계
    prompt = f"""
이 사진들을 보고 {style_preference} 톤으로 하루 일과를 기록해주세요.

참고할 촬영 정보:
{metadata_text}

작성 가이드라인:
1. 친구에게 하루 얘기하듯이 자연스럽고 편안한 톤으로 작성
2. 과도한 감성 표현이나 문학적 수사는 피하고, 실제 있었던 일들을 중심으로 서술
3. 시간, 장소, 활동, 함께한 사람들을 자연스럽게 포함
4. 사진들 간의 시간 순서를 고려하여 하루의 흐름을 보여주기
5. 적당한 분량으로 읽기 좋게 구성 (너무 길지도 짧지도 않게)

예시 톤:
- "오늘 오전에 공원에 갔다. 아이들과 함께 놀이터에서 놀았는데..."
- "점심 시간에 회사 근처 식당에서 동료들과 식사했다..."
- "저녁에는 집에서 가족과 함께 시간을 보냈다..."

일기처럼 쓰되, 과장되지 않고 실제 경험을 담은 자연스러운 기록을 만들어주세요.
"""
    
    try:
        # 텍스트 프롬프트와 이미지들을 함께 전송
        message_content = [{"type": "text", "text": prompt}] + image_contents
        
        response = model.invoke([HumanMessage(content=message_content)])
        
        return response.content
        
    except Exception as e:
        print(f"일기 생성 오류: {e}")
        return f"""
일상 기록 생성 중 오류가 발생했습니다: {str(e)}

오늘도 여러 가지 일들이 있었던 하루였습니다.
사진으로 남긴 순간들을 보면 나름 의미 있는 시간들을 보낸 것 같습니다.
비록 완전한 기록은 남기지 못했지만, 
이런 소소한 일상들이 모여 우리의 삶을 만들어가는 것 같습니다.
"""

def compare_diary_styles(image_paths: List[str]) -> Dict[str, str]:
    """
    다양한 스타일로 일기를 생성하여 비교
    """
    styles = {
        "감성적": "감성적이고 서정적인",
        "자연스러운": "자연스럽고 편안한", 
        "간결한": "간결하고 명확한",
        "상세한": "상세하고 구체적인"
    }
    
    results = {}
    
    for style_name, style_desc in styles.items():
        print(f"\n=== {style_name} 스타일 생성 중 ===")
        diary = generate_natural_diary(image_paths, style_desc)
        results[style_name] = diary
        print(f"완료: {len(diary)}자")
    
    return results

# 테스트 실행
if __name__ == "__main__":
    test_image_paths = [
        "test_images/photo1.jpeg",
        "test_images/photo2.jpeg", 
        "test_images/photo3.jpeg",
        "test_images/photo4.jpeg",

    ]
    
    if all(os.path.exists(path) for path in test_image_paths):
        print("=== 자연스러운 일상 기록 생성 테스트 ===")


    if all(os.path.exists(path) for path in test_image_paths):
        print("=== 다양한 스타일 일기 생성 테스트 ===")
        results = compare_diary_styles(test_image_paths)
        for style, diary in results.items():
            print(f"\n{'='*30}\n[{style} 스타일]\n{'='*30}")
            print(diary)
        print("테스트 완료!")
    else:
        print("❌ 테스트 이미지 파일이 존재하지 않습니다.")
        for path in test_image_paths:
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"   {exists} {path}")
    #     # 자연스러운 스타일로 일기 생성
    #     diary = generate_natural_diary(
    #         image_paths=test_image_paths,
    #         style_preference="자연스럽고 편안한"
    #     )
        
    #     print("\n" + "="*60)
    #     print("=== 생성된 일상 기록 (자연스러운 버전) ===")
    #     print("="*60)
    #     print(diary)
    #     print("="*60)
    #     print("테스트 완료!")
        
    # else:
    #     print("❌ 테스트 이미지 파일이 존재하지 않습니다.")
    #     for path in test_image_paths:
    #         exists = "✅" if os.path.exists(path) else "❌"
    #         print(f"   {exists} {path}")