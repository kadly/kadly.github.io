// Header.js
import React from 'react';
import styled from 'styled-components';
import { Link } from 'gatsby';

const HeaderContainer = styled.header`
  padding: 10px 20px; /* Уменьшаем вертикальные отступы */
  background: #333;/*eee Фон шапки */
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;

  /* Для экранов от 768px — располагаем три блока в строку */
  @media (min-width: 768px) {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
`;

/* Левый блок с логотипом */
const LeftContainer = styled.div`
  margin-bottom: 10px;
  /* Анимация появления */
  animation: fadeIn 1s ease-in-out;
  @media (min-width: 768px) {
    margin-bottom: 0;
  }
`;

/* Центральный блок с динамическим текстом */
const CenterContainer = styled.div`
  font-size: 2rem; /* базовый размер для мобильных устройств */
  margin-bottom: 10px;
  font-weight: 500;
  position: relative;
  top: -5px;
  background: linear-gradient(90deg, #ffb400, #ff7e00);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientAnimationSlow 8s ease infinite;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4);

  @media (min-width: 768px) {
    font-size: 2.5rem;
    margin-bottom: 0;
    flex-grow: 1;
    text-align: center;
    align-self: center;
  }

  @media (min-width: 1024px) {
    font-size: 4rem;
    margin-bottom: 0;
    flex-grow: 1;
    text-align: center;
    align-self: center;
  }

  @keyframes gradientAnimationSlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

/* Правый блок с контактной информацией */
const RightContainer = styled.div`
  /* Добавлено: разрешаем контейнеру сжиматься */
  min-width: 0;
  @media (min-width: 768px) {
    display: flex;
    align-items: center;
  }
`;

/* Блок ContactInfo также */
const ContactInfo = styled.div`
  text-align: center;
  min-width: 0;
  /* Экспериментальное свойство для балансировки переносов */
  text-wrap: balance;

  /* Фоллбэк‑стили */
  hyphens: none;
  word-break: normal;
  overflow-wrap: break-word;

  @media (min-width: 768px) {
    text-align: right;
  }
`;

const Logo = styled.h1`
  font-size: 4rem;
  margin: 0;
  font-weight: bold;
  letter-spacing: 0.4rem;
  background: linear-gradient(90deg, #a4ce4e, #b8e986);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientAnimation 5s ease infinite;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);

  @keyframes gradientAnimation {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  a {
    text-decoration: none;
    color: inherit;
    font-weight: bold;
  }
`;

const City = styled.p`
  margin: 0;
  font-size: 1.2rem;
  color: #eee;/*#333;*/
`;

const Phone = styled.a`
  display: block;
  margin: 5px 0;
  font-size: 1.2rem;
  color: #eee;/*#333;*/
  text-decoration: none;
  transition: color 0.3s ease;

  &:hover {
    color: #a4ce4e/*#006f3d;*/
  }
`;

const TelegramLink = styled.a`
  display: inline-flex;
  align-items: center;
  font-size: 1.2rem;
  color: #eee;/*#333;*/
  text-decoration: none;
  transition: color 0.3s ease;

  &:hover {
    color: #a4ce4e/*#006f3d;*/
  }
`;

const TelegramIcon = styled.img`
  width: 32px;
  height: 32px;
  margin-left: 8px;
  transform: translateY(1px); /* смещаем иконку вниз для лучшего выравнивания */
`;

const WhatsappLink = styled.a`
  display: inline-flex;
  align-items: center;
  font-size: 1.2rem;
  color: #eee;/*#333;*/
  text-decoration: none;
  transition: color 0.3s ease;
  margin-left: 15px; /* Added margin to separate from Telegram */

  &:hover {
    color: #a4ce4e/*#006f3d;*/
  }
`;

const WhatsappIcon = styled.img`
  width: 32px;
  height: 32px;
  margin-left: 8px;
  transform: translateY(1px); /* смещаем иконку вниз для лучшего выравнивания */
`;

const Header = ({ centerText }) => {
  return (
    <HeaderContainer>
      <LeftContainer>
        <Logo>
          <Link to="/">Zoomlio<span className="gradient">n</span></Link>
        </Logo>
      </LeftContainer>
      {centerText && (
        <CenterContainer>
          {centerText}
        </CenterContainer>
      )}
      <RightContainer>
        <ContactInfo>
          <City>г. Новосибирск</City>
          <Phone href="tel:+7-923-708-22-54">+7-923-708-22-54</Phone>
          <div>
            <TelegramLink
              href="https://t.me/gmitry"
              target="_blank"
              rel="noopener noreferrer"
            >
              <TelegramIcon
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"
                alt="Telegram logo"
              />
            </TelegramLink>
            <WhatsappLink
              href="https://wa.me/79237082254"
              target="_blank"
              rel="noopener noreferrer"
            >
              <WhatsappIcon
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/512px-WhatsApp.svg.png"
                alt="WhatsApp logo"
              />
            </WhatsappLink>
          </div>
        </ContactInfo>
      </RightContainer>
    </HeaderContainer>
  );
};

export default Header;

export const Head = () => (
  <>
    <title>Zoomlion</title>
    <link rel="icon" type="image/x-icon" href="/favicon.png" />
  </>
);
