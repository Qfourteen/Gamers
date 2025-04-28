import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Spinner, Alert } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

function CardGroup() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch('/data/card')
      .then((res) => {
        if (!res.ok) {
          throw new Error('서버 응답 오류');
        }
        return res.json();
      })
      .then((data) => {
        setCards(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('카드 데이터 불러오기 실패:', err);
        setError('카드 데이터를 불러오는 중 오류가 발생했습니다.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <Container className="text-center my-5">
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">로딩 중...</span>
        </Spinner>
        <p className="mt-2">게임 데이터를 불러오는 중입니다...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="my-5">
        <Alert variant="danger">
          <Alert.Heading>오류 발생</Alert.Heading>
          <p>{error}</p>
        </Alert>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <Row xs={1} sm={2} md={3} lg={4} className="g-4">
        {cards.map((card, idx) => (
          <Col key={idx}>
            <Card
              as="a"
              href={card.game_id}
              target="_blank"
              rel="noopener noreferrer"
              className="h-100 text-decoration-none"
            >
              <Card.Img variant="top" src={card.image_url} alt={card.card_title} />
              <Card.Body>
                <Card.Subtitle className="mb-2 text-muted">{card.name}</Card.Subtitle>
                <Card.Title>{card.card_title}</Card.Title>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
}

export default CardGroup;