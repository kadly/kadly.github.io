import React from 'react';
import styled from 'styled-components';
import { GatsbyImage } from "gatsby-plugin-image";

const Card = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #fff;
  padding: 16px;
  cursor: pointer;
  width: 300px; /* Фиксированная ширина карточки */
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ImageContainer = styled.div`
  width: 100%;
  height: 200px;  /* Фиксированная высота для области изображения */
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eee;
  margin-bottom: 10px;
`;

const Placeholder = styled.span`
  font-size: 14px;
  color: #666;
`;

const ModelCard = ({ name, imageData, onClick }) => {
  return (
    <Card onClick={onClick}>
      <ImageContainer>
        {imageData ? (
          <GatsbyImage
            image={imageData}
            alt={name}
            style={{ width: '100%', height: '100%' }}
            imgStyle={{ objectFit: 'contain' }}
          />
        ) : (
          <Placeholder>Нет фото</Placeholder>
        )}
      </ImageContainer>
      <h3>{name}</h3>
    </Card>
  );
};

export default ModelCard;