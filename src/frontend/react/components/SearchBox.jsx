import React, { useState } from 'react';

function SearchBox({ onSearchResults }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`/data/search?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((data) => {
        onSearchResults(data);
      })
      .catch((err) => {
        console.error('검색 오류:', err);
      });
  };

  return (
    <form onSubmit={handleSubmit} className="mb-3">
      <div className="input-group">
        <input
          type="text"
          className="form-control"
          placeholder="검색어를 입력하세요"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="btn btn-primary">
          검색
        </button>
      </div>
    </form>
  );
}

export default SearchBox;
