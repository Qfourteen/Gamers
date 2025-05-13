from datetime import datetime, timezone
import regex
import re


def utc_now_factory(tz=timezone.utc):
    return datetime.now(tz)


def filter_nickname_characters(text):
    if not text:
        return ""
    
    # 키보드로 입력 가능한 특수문자 목록
    keyboard_special_chars = r'`~!@#$%^&*()-_=+[{]}\\|;:\'",./?'
    
    # 첫 번째 글자는 문자(알파벳, 한글, 한자 등)만 허용
    first_char = text[0]
    first_filtered = regex.sub(r'[^\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}]', '', first_char)
    
    # 첫 번째 글자 이후 문자들은 문자, 숫자, 키보드 특수문자 허용
    rest_text = text[1:] if len(text) > 1 else ""
    rest_filtered = regex.sub(r'[^\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}0-9' + re.escape(keyboard_special_chars) + ']', '', rest_text)
    
    # 결과 조합
    filtered = first_filtered + rest_filtered
    
    return filtered


def is_valid_nickname(text):
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
    if first_char.isdigit() or not regex.match(r'[\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}]', first_char):
        return False
    
    return True
