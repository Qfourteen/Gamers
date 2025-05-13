import re


def is_valid_password(password: str) -> bool:
    """
    비밀번호가 유효한지 검증합니다.
    
    필수 요구사항:
    - 최소 6자 이상
    - 최대 200자 이하
    
    권장사항 (필수 아님):
    - 문자, 숫자, 특수문자 포함
    - 대소문자 혼합
    
    Args:
        password (str): 검증할 비밀번호
        
    Returns:
        bool: 비밀번호가 유효하면 True, 그렇지 않으면 False
    """
    # 기본 길이 검증 (유일한 필수 요구사항)
    if password is None or not (6 <= len(password) <= 200):
        return False
    
    return True


def get_password_strength(password: str) -> dict:
    """
    비밀번호의 강도를 평가합니다.
    
    필수 요구사항은 길이 검증만 적용하고, 
    나머지는 권장사항으로 평가합니다.
    
    Args:
        password (str): 평가할 비밀번호
        
    Returns:
        dict: 비밀번호 강도와 관련된 정보
    """
    score = 0
    feedback = []
    
    # 비밀번호가 없는 경우
    if password is None:
        return {
            "score": 0,
            "strength": "입력 없음",
            "color": "secondary",
            "feedback": ["비밀번호를 입력해주세요."],
            "is_valid": False
        }
    
    # 길이 검증 (필수 요구사항)
    length = len(password)
    if length < 6:
        feedback.append("비밀번호는 최소 6자 이상이어야 합니다.")
        return {
            "score": 0,
            "strength": "유효하지 않음",
            "color": "danger",
            "feedback": feedback,
            "is_valid": False
        }
    elif length > 200:
        feedback.append("비밀번호는 최대 200자 이하여야 합니다.")
        return {
            "score": 0,
            "strength": "유효하지 않음",
            "color": "danger",
            "feedback": feedback,
            "is_valid": False
        }
    
    # 여기서부터는 권장사항 기반 강도 측정
    
    # 길이 점수
    if length < 10:
        score += 1
    elif length < 14:
        score += 2
    else:
        score += 3
    
    # 문자 포함 여부
    has_lowercase = re.search(r'[a-z]', password)
    has_uppercase = re.search(r'[A-Z]', password)
    
    if has_lowercase:
        score += 1
    if has_uppercase:
        score += 1
    
    if not (has_lowercase and has_uppercase):
        feedback.append("대소문자를 모두 포함하면 더 안전합니다.")
    
    # 숫자 포함 여부
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("숫자를 포함하면 더 안전합니다.")
    
    # 특수문자 포함 여부
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("특수문자를 포함하면 더 안전합니다.")
    
    # 다양한 문자 사용 여부
    if len(set(password)) > 10:
        score += 1
    
    # 점수에 따른 강도 결정
    strength = "매우 약함"
    color = "danger"
    
    if score >= 7:
        strength = "매우 강함"
        color = "success"
    elif score >= 5:
        strength = "강함"
        color = "primary"
    elif score >= 3:
        strength = "보통"
        color = "warning"
    elif score >= 1:
        strength = "약함"
        color = "danger"
    
    # 최종 피드백
    if not feedback and score < 5:
        feedback.append("더 길고 복잡한 비밀번호를 사용하면 더 안전합니다.")
    
    return {
        "score": score,
        "strength": strength,
        "color": color,
        "feedback": feedback,
        "is_valid": True  # 길이 요구사항을 충족하면 항상 유효
    }


def get_password_validation_rules() -> dict:
    """
    비밀번호 유효성 검증 규칙을 반환합니다.
    
    Returns:
        dict: 비밀번호 유효성 검증 규칙
    """
    return {
        "requirements": [
            "비밀번호는 최소 6자 이상이어야 합니다.",
            "비밀번호는 최대 200자 이하여야 합니다."
        ],
        "recommendations": [
            "대소문자 모두 포함하는 것을 권장합니다.",
            "숫자(0-9)를 포함하는 것을 권장합니다.", 
            "특수문자(!@#$%^&*(),.?\":{}|<>)를 포함하는 것을 권장합니다.",
        ],
        "strength_guide": [
            {"level": "매우 약함", "description": "매우 쉽게 해킹될 수 있는 비밀번호입니다."},
            {"level": "약함", "description": "기본적인 요구사항만 충족하는 비밀번호입니다."},
            {"level": "보통", "description": "일반적인 해킹 시도에 어느 정도 안전합니다."},
            {"level": "강함", "description": "대부분의 해킹 시도에 안전한 비밀번호입니다."},
            {"level": "매우 강함", "description": "매우 안전한 비밀번호입니다."}
        ]
    }
