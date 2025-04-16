import React from 'react';

function SearchResultsTable({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-muted">검색 결과가 없습니다.</div>;
  }

  return (
    <table className="table table-hover table-bordered">
      <thead className="table-light">
        <tr>
          <th>제목</th>
          <th>내용</th>
          <th>태그</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            <td>
              <a href={row.game_id} className="text-decoration-none">
                {row.name}
              </a>
            </td>
            <td>{row.short_description}</td>
            <td>
              {row.tags.length > 0 ? (
                row.tags.map((tag, tagIdx) => (
                  <span key={tagIdx} className="badge bg-secondary me-1">
                    {tag}
                  </span>
                ))
              ) : (
                <span className="text-muted">없음</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default SearchResultsTable;
