// Footer.js
import React from 'react';
import styled from 'styled-components';

// Стили для контейнера футера
const FooterContainer = styled.footer`
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 10px;
  background: #333;
  color: white;
  margin-top: auto;
  font-size: 16px;

  p {
    margin: 0; /* Убираем стандартный отступ у параграфа */
  }

  /* Медиазапрос для устройств с шириной экрана до 768px (планшеты) */
  @media (max-width: 768px) {
    font-size: 14px;
    padding: 8px;
  }

  /* Медиазапрос для устройств с шириной экрана до 480px (мобильные) */
  @media (max-width: 480px) {
    font-size: 12px;
    padding: 5px;
  }
`;

const Footer = ({ companyName, /*yearsActive,*/ websiteUrl }) => {
  const currentYear = new Date().getFullYear();
  const establishedYear = 2000; // Год основания компании
  const yearsActive = currentYear - establishedYear; // Автоматически вычисляем число лет
  return (
    <FooterContainer>
      <p>
        &copy; {currentYear} {companyName}. {yearsActive} лет на мировом рынке.
        {/*{websiteUrl && (
          <span>
            &nbsp;
            <a href={websiteUrl} target="_blank" rel="noopener noreferrer">
              Наш сайт
            </a>
          </span>
        )}*/}
      </p>
    </FooterContainer>
  );
};

export default Footer;