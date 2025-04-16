import React, { useState } from 'react';
import SearchBox from './SearchBox';
import SearchResultsTable from './SearchResultsTable';
import CardGroup from './CardGroup';

function Home() {
  // 검색 결과를 상태로 관리
  const [searchResults, setSearchResults] = useState([]);

  return (
    <div className="container mt-4">
      <h1 className={"text-center"}>Gamers</h1>

        {/* 검색창 */}
        <SearchBox onSearchResults={setSearchResults} />

        {/* 검색 결과 표 */}
        <SearchResultsTable data={searchResults} />

        {/* 카드 그룹 */}
      <CardGroup />
    </div>
  );
}

export default Home;
