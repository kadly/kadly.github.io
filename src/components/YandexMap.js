import React from 'react';

const YandexMap = () => {
  return (
    <div style={{position: 'relative', overflow: 'hidden', margin: '40px auto 20px auto', maxWidth: '1200px', padding: '0 20px', boxSizing: 'border-box'}}>
      <div style={{position: 'relative', overflow: 'hidden', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'}}>
        <iframe
          title="Яндекс Карта"
          src="https://yandex.ru/map-widget/v1/?um=constructor%3A63541402cb36537952d86ae80e2afa656afd7fd7c7fa7f8f25a8612de8a28084&source=constructor"
          width="100%"
          height="265"
          frameBorder="0"
          style={{position: 'relative', border: 'none', display: 'block'}}>
        </iframe>
      </div>
    </div>
  );
};

export default YandexMap;
