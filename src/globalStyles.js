// src/globalStyles.js
import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  /* Применяем box-sizing для всех элементов */
  *, *::before, *::after {
    box-sizing: border-box;
  }

  /* Сброс отступов для body, если требуется */
  body {
    margin: 0;
    padding: 0;
    background-color: #ffffff; /* Основной цвет фона - белый */
    background-image: repeating-linear-gradient(
      45deg,
      transparent,
      transparent 35px,
      rgba(0, 0, 0, 0.03) 35px,
      rgba(0, 0, 0, 0.03) 70px
    ); /* Легкий узор */
  }
`;

export default GlobalStyle;
