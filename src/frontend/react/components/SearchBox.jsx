import React, { useState } from 'react';
import { Form, InputGroup, Button, Container, Spinner, Alert } from 'react-bootstrap';
import { FaSearch } from 'react-icons/fa';

/**
 * 검색 기능을 제공하는 컴포넌트
 * @param {function} onSearchResults - 검색 결과를 부모 컴포넌트로 전달하는 콜백 함수
 */
function SearchBox({ onSearchResults }) {
  // 상태 관리 변수들
  const [query, setQuery] = useState('');                  // 검색어
  const [isLoading, setIsLoading] = useState(false);       // 로딩 상태
  const [error, setError] = useState(null);                // 오류 메시지
  const [searchState, setSearchState] = useState('initial'); // 검색 상태 (initial, searched, no-results, error)

  /**
   * 검색 폼 제출 시 실행되는 함수
   * @param {Event} e - 폼 제출 이벤트
   */
  const handleSubmit = (e) => {
    // 폼 기본 제출 동작 방지
    e.preventDefault();

    // 빈 검색어 검사
    if (!query.trim()) {
      return; // 검색어가 비어있으면 함수 종료
    }

    // 로딩 상태 시작 및 이전 오류 초기화
    setIsLoading(true);
    setError(null);

    // 검색 API 호출
    fetch(`/data/search?q=${encodeURIComponent(query)}`)
      .then((res) => {
        // HTTP 응답 상태 확인
        if (!res.ok) {
          throw new Error('검색 결과를 불러올 수 없습니다');
        }
        return res.json(); // JSON 형태로 변환
      })
      .then((data) => {
        // 검색 결과 처리
        if (data && data.length === 0) {
          // 검색 결과가 없는 경우
          setSearchState('no-results');
        } else {
          // 검색 결과가 있는 경우
          setSearchState('searched');
        }

        // 부모 컴포넌트에 결과 전달 및 로딩 상태 종료
        onSearchResults(data);
        setIsLoading(false);
      })
      .catch((err) => {
        // 오류 처리
        console.error('검색 오류:', err);
        setError('검색 중 오류가 발생했습니다.');
        setIsLoading(false);
        setSearchState('error');
        onSearchResults([]);
      });
  };

  /**
   * 검색어 입력 변경 시 실행되는 함수
   * @param {Event} e - 입력 변경 이벤트
   */
  const handleQueryChange = (e) => {
    const newQuery = e.target.value;
    setQuery(newQuery);

    // 검색어가 비어있고 이전에 검색한 상태였다면 초기 상태로 변경
    if (newQuery.trim() === '' && searchState !== 'initial') {
      setSearchState('initial');
      onSearchResults([]); // 결과 초기화
    }
  };

  // 검색 버튼 내용 결정 함수
  const renderButtonContent = () => {
    if (isLoading) {
      return (
        <>
          <Spinner
            as="span"
            animation="border"
            size="sm"
            className="me-1"
          />
          검색 중...
        </>
      );
    }

    return (
      <>
        <FaSearch className="me-1" /> 검색
      </>
    );
  };

  return (
    <Container className={"py-3"}>
      {/* 검색 폼 */}
      <Form onSubmit={handleSubmit}>
        <InputGroup className="mb-3 shadow-sm">
          {/* 검색어 입력 필드 */}
          <Form.Control
            type="text"
            placeholder="검색어를 입력하세요"
            value={query}
            onChange={handleQueryChange}
            disabled={isLoading}
            isInvalid={error !== null}
          />

          {/* 검색 버튼 */}
          <Button
            variant="primary"
            type="submit"
            disabled={isLoading || !query.trim()}
          >
            {renderButtonContent()}
          </Button>
        </InputGroup>

        {/* 오류 메시지 표시 */}
        {error && (
          <Form.Text className="text-danger">
            {error}
          </Form.Text>
        )}
      </Form>

      {/* 검색 결과 없음 메시지 */}
      {searchState === 'no-results' && (
        <Alert variant="info" className="mt-3">
          <Alert.Heading>검색 결과 없음</Alert.Heading>
          <p>
            <strong>"{query}"</strong>에 대한 검색 결과가 없습니다. 다른 검색어로 시도해 보세요.
          </p>
        </Alert>
      )}

      {/* 초기 화면 안내 메시지 */}
      {searchState === 'initial' && query.trim() === '' && (
        <div className="text-center my-5 py-5 text-muted">
          <FaSearch size={48} className="mb-3 opacity-50" />
          <h4>무엇이든 검색해보세요!</h4>
          <p className="text-secondary">검색창에 키워드를 입력하여 게임을 찾아보세요.</p>
        </div>
      )}
    </Container>
  );
}

export default SearchBox;