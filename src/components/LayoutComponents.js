import styled from 'styled-components';

export const Layout = styled.div`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
`;

export const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  flex: 1 0 auto;
`;

// Изменённый компонент Grid для центрирования карточек
export const Grid = styled.div`
  display: grid;
  /* Используем auto-fit для адаптивности и центрирования карточек */
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px 8px; /* 16px для вертикального отступа и 8px для горизонтального */
  justify-items: center; /* Центрирование содержимого каждой ячейки */
  justify-content: center; /* Центрирование всей сетки внутри контейнера */
  padding: 20px;
`;

// Дополнительный стиль для вывода удобочитаемого названия выбранной модели
export const Subtitle = styled.p`
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  margin-top: 1rem;
`;
