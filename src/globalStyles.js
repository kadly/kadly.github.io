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
  }
`;

export default GlobalStyle;
