import React from 'react';

function SearchResultsTable({ data }) {
  if (!data || data.length === 0) {
    return <div>검색 결과가 없습니다.</div>;
  }

  return (
    <table border="1" cellPadding="5" style={{ marginBottom: '2rem' }}>
      <thead>
        <tr>
          <th>제목</th>
          <th>내용</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            <td>{row.title}</td>
            <td>{row.content}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default SearchResultsTable;
