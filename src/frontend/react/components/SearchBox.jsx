import React, { useState } from 'react';

function SearchBox({ onSearchResults }) {
  const [query, setQuery] = useState('');

  // 폼 제출 시 서버에 fetch
  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`/data/search?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((data) => {
        // 부모(Home) 컴포넌트로 결과 전달
        onSearchResults(data);
      })
      .catch((err) => {
        console.error('검색 오류:', err);
      });
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <input
        type="text"
        placeholder="검색어를 입력하세요"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button type="submit">검색</button>
    </form>
  );
}

export default SearchBox;
