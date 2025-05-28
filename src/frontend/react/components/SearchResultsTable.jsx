import React from 'react';
import { Table, Badge, Alert, Card, Container } from 'react-bootstrap';
import { FaExternalLinkAlt, FaTag } from 'react-icons/fa'; // 선택 사항

function SearchResultsTable({ data }) {
  if (!data || data.length === 0) {
    return (
      <Alert variant="info" className="text-center my-4">
        <Alert.Heading>검색 결과 없음</Alert.Heading>
        <p className="mb-0">검색 조건에 맞는 결과를 찾을 수 없습니다. 다른 검색어로 시도해 보세요.</p>
      </Alert>
    );
  }

  return (
    <Container className="py-3">
      <Card className="shadow-sm">
        <Card.Header className="bg-primary-subtle">
          <strong>검색 결과: {data.length}개</strong>
        </Card.Header>
        <Table responsive hover bordered className="mb-0">
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
                    {row.name}
                    <FaExternalLinkAlt className="ms-1 text-muted" size={12} />
                </td>
                <td>
                  {row.short_description || (
                    <span className="text-muted fst-italic">내용 없음</span>
                  )}
                </td>
                <td>
                  {row.tags && row.tags.length > 0 ? (
                    <div className="d-flex flex-wrap gap-1">
                      {row.tags.map((tag, tagIdx) => (
                        <Badge
                          key={tagIdx}
                          bg="dark"
                          className="d-flex align-items-center"
                          onClick={() => window.open(`/tag/${tag}`, '_blank')}
                          style={{ cursor: 'pointer' }}
                        >
                          <FaTag className="me-1" size={10} />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <span className="text-muted fst-italic">태그 없음</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </Container>
  );
}

export default SearchResultsTable;