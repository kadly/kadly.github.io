import React from 'react';

const YandexMap = () => {
  return (
    <div style={{position: 'relative', overflow: 'hidden', margin: '40px auto 20px auto', maxWidth: '960px', padding: '0 20px', boxSizing: 'border-box'}}>
      <div style={{position: 'relative', overflow: 'hidden', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'}}>
        <a href="https://yandex.ru/maps/65/novosibirsk/?utm_medium=mapframe&utm_source=maps" style={{color: '#eee', fontSize: '12px', position: 'absolute', top: '0px', zIndex: 1}}>Новосибирск</a>
        <a href="https://yandex.ru/maps/65/novosibirsk/?ll=82.775838%2C54.997488&mode=whatshere&utm_medium=mapframe&utm_source=maps&whatshere%5Bpoint%5D=82.777067%2C54.998330&whatshere%5Bzoom%5D=17.32&z=17.32" style={{color: '#eee', fontSize: '12px', position: 'absolute', top: '14px', zIndex: 1}}>Станционная улица, 86/5 — Яндекс Карты</a>
        <iframe
          title="Яндекс Карта с местоположением офиса"
          src="https://yandex.ru/map-widget/v1/?ll=82.775838%2C54.997488&mode=whatshere&whatshere%5Bpoint%5D=82.777067%2C54.998330&whatshere%5Bzoom%5D=17.32&z=17.32"
          width="100%"
          height="400"
          frameBorder="0"
          allowFullScreen={true}
          style={{position: 'relative', border: 'none', display: 'block'}}>
        </iframe>
      </div>
    </div>
  );
};

export default YandexMap;
