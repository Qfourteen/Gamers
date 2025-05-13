import pytest
import regex
import re
from src.backend.utility.nickname_utils import filter_nickname_characters, is_valid_nickname

class TestFilterNicknameCharacters:
    """Tests for the filter_nickname_characters function."""
    
    def test_first_character_filtering(self):
        """Test that the first character filtering works correctly."""
        # First character should remain if it's a letter
        assert filter_nickname_characters("Hello")[0] == "H"
        assert filter_nickname_characters("안녕하세요")[0] == "안"
        assert filter_nickname_characters("你好")[0] == "你"
        
        # First character should be removed if it's a number or special character
        assert filter_nickname_characters("123abc") == "23abc"
        assert filter_nickname_characters("!Hello") == "Hello"
        assert filter_nickname_characters("@User") == "User"
        
    def test_allowed_characters_in_first_position(self):
        """Test that only allowed scripts are preserved in the first position."""
        # Various scripts should be allowed in first position
        scripts = [
            "abcdef",           # Latin
            "안녕하세요",        # Korean (Hangul)
            "你好世界",          # Chinese
            "こんにちは",        # Japanese (Hiragana)
            "コンニチハ",        # Japanese (Katakana)
            "привет",           # Cyrillic
            "γειασας",          # Greek
            "שלום",             # Hebrew
            "مرحبا",            # Arabic
            "नमस्ते",           # Devanagari
            "สวัสดี",           # Thai
            "Բարեւ",            # Armenian
            "გამარჯობა"         # Georgian
        ]
        
        for script in scripts:
            assert filter_nickname_characters(script) == script
    
    def test_allowed_characters_after_first_position(self):
        """Test that letters, numbers, and keyboard special characters are allowed after first position."""
        # Standard letters and numbers
        assert filter_nickname_characters("A123abc") == "A123abc"
        
        # All keyboard special characters after a valid first character
        keyboard_special_chars = "`~!@#$%^&*()-_=+[{]}\\|;:'\",./?"
        test_str = "A" + keyboard_special_chars + "123abc"
        assert filter_nickname_characters(test_str) == test_str
        
        # Test with mix of scripts and special characters
        assert filter_nickname_characters("A안녕!@#$%") == "A안녕!@#$%"
        assert filter_nickname_characters("안!@#$%^&*()") == "안!@#$%^&*()"
        assert filter_nickname_characters("Hello!123@#$") == "Hello!123@#$"
    
    def test_disallowed_characters_removal(self):
        """Test that disallowed characters are properly removed."""
        # Emoji removal
        assert filter_nickname_characters("User😊") == "User"
        assert filter_nickname_characters("A😊B😊C") == "ABC"
        
        # Control characters removal
        assert filter_nickname_characters("User\u0000\u0001\u0002") == "User"
        
        # Whitespace removal
        assert filter_nickname_characters("User Name") == "UserName"
        assert filter_nickname_characters("Tab\tNewline\n") == "TabNewline"
    
    def test_edge_cases(self):
        """Test edge cases for the filter_nickname_characters function."""
        # Empty string
        assert filter_nickname_characters("") == ""
        
        # String with only disallowed first characters
        assert filter_nickname_characters("12345") == "2345"
        assert filter_nickname_characters("!@#$%") == "@#$%"
        
        # String with disallowed first character but allowed following characters
        assert filter_nickname_characters("!abc") == "abc"
        
        # String with only emoji
        assert filter_nickname_characters("😊😊😊") == ""
        
        # Mixed valid and invalid characters
        assert filter_nickname_characters("A😊b!c😊d") == "Ab!cd"


class TestIsValidNickname:
    """Tests for the is_valid_nickname function."""
    
    def test_valid_nicknames(self):
        """Test various valid nickname formats."""
        valid_nicknames = [
            "User123",              # Basic alphanumeric
            "안녕하세요",            # Korean only
            "User!@#$%",            # With special chars
            "A_B-C.D@E",            # With allowed punctuation
            "Hello世界",            # Mixed scripts
            "Abc123!@#",            # Mixed alphanumeric and special
            "안녕123!@#",           # Korean with numbers and special
            "Abcdefghijklmn",       # Longer name
            "A123",                 # Minimal valid (letter + numbers)
            "Aa"                    # Minimal valid (just letters)
        ]
        
        for nickname in valid_nicknames:
            assert is_valid_nickname(nickname) == True, f"Expected {nickname} to be valid"
    
    def test_invalid_nicknames_first_character(self):
        """Test invalid nicknames where the first character is not a letter."""
        invalid_first_char = [
            "123User",              # Starts with number
            "!User",                # Starts with special character
            "@User",                # Starts with special character
            "_User",                # Starts with underscore
            "123안녕",              # Starts with number before Korean
            "!안녕하세요",          # Starts with special before Korean
            ".abc",                 # Starts with period
            "-Testing"              # Starts with hyphen
        ]
        
        for nickname in invalid_first_char:
            assert is_valid_nickname(nickname) == False, f"Expected {nickname} to be invalid"
    
    def test_invalid_nicknames_disallowed_characters(self):
        """Test invalid nicknames containing disallowed characters."""
        invalid_chars = [
            "User😊",               # Contains emoji
            "안녕👋하세요",         # Contains emoji
            "User\u0000abc",        # Contains control character
            "Test\t\nName",         # Contains whitespace
            "User Name",            # Contains space
            "Test<script>",         # Contains HTML-like content
        ]
        
        for nickname in invalid_chars:
            assert is_valid_nickname(nickname) == False, f"Expected {nickname} to be invalid"
    
    def test_invalid_nicknames_other_cases(self):
        """Test other invalid nickname cases."""
        other_invalid = [
            "",                     # Empty string
            " ",                    # Just whitespace
            "😊😊😊",              # Only emoji
            "!!!",                  # Only special chars
            "123",                  # Only numbers
        ]
        
        for nickname in other_invalid:
            assert is_valid_nickname(nickname) == False, f"Expected {nickname} to be invalid"
    
    def test_filtering_consistency(self):
        """Test that is_valid_nickname correctly validates filtered nicknames."""
        # These should be invalid because they would be modified by filtering
        inconsistent_nicknames = [
            "User!Name",            # If spaces are removed in filtering
            "Hello😊World",         # If emoji are removed in filtering
            "A\u0000B\u0000C",      # If control chars are removed in filtering
        ]
        
        for nickname in inconsistent_nicknames:
            filtered = filter_nickname_characters(nickname)
            if filtered != nickname:
                assert is_valid_nickname(nickname) == False, f"Expected {nickname} to be invalid because it would be filtered to {filtered}"