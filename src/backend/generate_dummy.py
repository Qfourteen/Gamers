from src.backend.schemas.game_list import SearchResult, CardResult
from typing import List, Optional

def get_data_search() -> List[SearchResult]:
    search1 = SearchResult(
        name="search sample1",
        short_description="search sample1은 아주 재밌습니다.",
        tags=["fps", "adventure"],
        game_id="https://github.com/Qfourteen"
    )
    search2 = SearchResult(
        name="search sample2",
        short_description="search sample2은 아주 재밌습니다.",
        tags=["fps"],
        game_id="https://github.com/Qfourteen"
    )
    search3 = SearchResult(
        name="search sample3",
        short_description="search sample2은 아주 재밌습니다.",
        tags=[],
        game_id="https://github.com/Qfourteen"
    )
    return [search1, search2, search3]


def get_data_card() -> List[CardResult]:
    # 샘플 base64 이미지 (작은 투명 PNG)
    sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAADMElEQVR4nOzVwQnAIBQFQYXff81RUkQCOyDj1YOPnbXWPmeTRef+/3O/OyBjzh3CD95BfqICMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMO0TAAD//2Anhf4QtqobAAAAAElFTkSuQmCC"
    
    card1 = CardResult(
        name="card sample1",
        card_title="지금 당장 플레이하세요",
        image_base64=sample_base64,
        game_id="https://github.com/Qfourteen"
    )
    card2 = CardResult(
        name="card sample2",
        card_title="게임 커뮤니티를 흔든 바로 그 게임",
        image_base64=sample_base64,
        game_id="https://github.com/Qfourteen"
    )
    card3 = CardResult(
        name="card sample3",
        card_title="영광은 영원하다",
        image_base64=sample_base64,
        game_id="https://github.com/Qfourteen"
    )
    card4 = CardResult(
        name="card sample4",
        card_title="달콤한 꿈",
        image_base64=sample_base64,
        game_id="https://github.com/Qfourteen"
    )
    return [card1, card2, card3, card4]