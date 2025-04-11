import React, { useEffect, useState } from 'react';

function CardGroup() {
  const [cards, setCards] = useState([]);

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
    <div className="row g-4">
      {cards.map((card, idx) => (
        <a
            href={card.game_id}
            target="_blank"
            className="col-sm-6 col-md-4 col-lg-3 text-decoration-none text-dark"
            key={idx}
        >
            <div className="card h-100">
              <img src={card.image_url} className="card-img-top" alt={card.card_title} />
              <div className="card-body">
                <small className="text-muted">{card.name}</small>
                <h5 className="card-title">{card.card_title}</h5>
              </div>
            </div>
        </a>
      ))}
    </div>
  );
}

export default CardGroup;
