import regex
import re


def filter_nickname_characters(text):
    """
    닉네임에 사용되는 문자를 필터링합니다.

    첫 번째 글자는 문자(알파벳, 한글, 한자 등)만 허용하고,
    이후는 문자, 숫자, 키보드 특수문자를 허용합니다.

    Args:
        text (str): 필터링할 텍스트

    Returns:
        str: 필터링된 텍스트
    """
    if not text:
        return ""

    # 키보드로 입력 가능한 특수문자 목록
    keyboard_special_chars = r'`~!@#$%^&*()-_=+[{]}\\|;:\'",./?'

    # 첫 번째 글자는 문자(알파벳, 한글, 한자 등)만 허용
    first_char = text[0]
    first_filtered = regex.sub(
        r'[^\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}]',
        '', first_char)

    # 첫 번째 글자 이후 문자들은 문자, 숫자, 키보드 특수문자 허용
    rest_text = text[1:] if len(text) > 1 else ""
    rest_filtered = regex.sub(
        r'[^\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}0-9' + re.escape(
            keyboard_special_chars) + ']', '', rest_text)

    # 결과 조합
    filtered = first_filtered + rest_filtered

    return filtered


def is_valid_nickname(text):
    """
    주어진 텍스트가 유효한 닉네임인지 검증합니다.

    - 첫 글자는 반드시 문자(알파벳, 한글, 한자 등)여야 함
    - 필터링 전후 텍스트가 동일해야 함 (허용되지 않는 문자가 없어야 함)
    - 비어있지 않아야 함

    Args:
        text (str): 검증할 텍스트

    Returns:
        bool: 유효한 닉네임이면 True, 아니면 False
    """
    # 길이 조건
    if len(text) < 3 or len(text) > 100:
        return False
    filtered = filter_nickname_characters(text)
    # 필터링 결과가 비었거나, 필터링 전후가 다르면 유효하지 않다고 판단
    if not filtered:
        return False
    if filtered != text:
        return False

    # 첫 글자가 문자(알파벳, 한글, 한자 등)인지 확인
    first_char = filtered[0] if filtered else ""
    if not first_char:
        return False

    # 첫 글자가 숫자나 특수문자가 아닌지 확인
    if first_char.isdigit() or not regex.match(
            r'[\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}]',
            first_char):
        return False

    return True


def get_nickname_validation_rules():
    """
    닉네임 유효성 검증 규칙을 문자열로 반환합니다.

    Returns:
        dict: 닉네임 유효성 검증 규칙
    """
    return {
        "rules": [
            "ID는 3글자 이상, 100글자 이하여야 합니다.",
            "첫 글자는 반드시 문자(알파벳, 한글, 한자 등)여야 합니다.",
            "이후 글자는 문자, 숫자, 키보드 특수문자를 사용할 수 있습니다.",
            "이모지, 공백, 제어 문자는 사용할 수 없습니다."
        ],
        "allowed_scripts": [
            "Latin (알파벳)",
            "Hangul (한글)",
            "Han (한자)",
            "Hiragana, Katakana (일본어)",
            "Cyrillic (러시아어)",
            "Greek (그리스어)",
            "Hebrew (히브리어)",
            "Arabic (아랍어)",
            "Devanagari (힌디어 등)",
            "Thai (태국어)",
            "Armenian (아르메니아어)",
            "Georgian (조지아어)"
        ],
        "special_chars": "`~!@#$%^&*()-_=+[{]}\\|;:'\",./?"
    }
