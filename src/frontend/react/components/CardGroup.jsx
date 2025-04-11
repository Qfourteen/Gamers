import React, { useEffect, useState } from 'react';

function CardGroup() {
  const [cards, setCards] = useState([]);

  // 마운트 시 /data/card에서 카드 목록 가져오기
  useEffect(() => {
    fetch('/data/card')
      .then((res) => res.json())
      .then((data) => {
        setCards(data);
      })
      .catch((err) => {
        console.error('카드 데이터 불러오기 실패:', err);
      });
  }, []);

  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      {cards.map((card, idx) => (
        <div key={idx} style={{
          border: '1px solid #ccc',
          padding: '1rem',
          width: '200px'
        }}>
          <h3>{card.title}</h3>
          <p>{card.description}</p>
        </div>
      ))}
    </div>
  );
}

export default CardGroup;
