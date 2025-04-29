from datetime import datetime, timezone
import regex


def utc_now_factory(tz=timezone.utc):
    return datetime.now(tz)


def filter_nickname_characters(text):
    # 먼저 허용되는 문자만 남김
    filtered = regex.sub(r'[^\p{Latin}\p{Han}\p{Hangul}\p{Hiragana}\p{Katakana}\p{Cyrillic}\p{Greek}\p{Hebrew}\p{Arabic}\p{Devanagari}\p{Thai}\p{Armenian}\p{Georgian}0-9@_.-]', '', text)

    return filtered


def is_valid_nickname(text):
    filtered = filter_nickname_characters(text)
    # 필터링 결과가 비었거나, 필터링 전후가 다르면 유효하지 않다고 판단
    if not filtered:
        return False
    if filtered != text:
        return False
    if filtered[0].isdigit():
        return False
    if filtered[0] in {'_', '-', '@', '.'}:
        return False
    return True
