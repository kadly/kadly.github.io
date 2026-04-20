import React from 'react';
import styled from 'styled-components';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  max-width: 450px; /* Немного уменьшаем ширину окна */
  width: 100%;
  position: relative;
  text-align: center; /* Центрируем заголовок и логотипы */
`;

const IconsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const Icon = styled.img`
  width: 40px;
  height: 40px;
`;

const ModelText = styled.div`
  margin: 1rem 0;
  font-size: 16px;
  
  /* Заголовок модели оставляем по центру */
  h3 {
    text-align: center;
  }
  
  /* Список отображаем как блок, выровненный по левому краю */
  ul {
    list-style: none;
    padding: 0;
    margin: 0 auto;
    max-width: 90%;
    text-align: left;
  }
  
  li {
    /* Пункты списка по умолчанию выравниваются по левому краю */
    margin-bottom: 0.5rem;
  }
`;

const CloseButton = styled.button`
  background: #006f3d;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;

  &:hover {
    background: #00532d;
  }
`;

const ModalContact = ({ isOpen, onClose, ModelComponent }) => {
  if (!isOpen) {
    return null;
  }

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <h2>Связаться с продавцом</h2>
        <IconsContainer>
          <a href="https://telegram.me/gmitry" target="_blank" rel="noopener noreferrer">
            <Icon src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram" />
          </a>
          <a href="https://wa.me/7231280168" target="_blank" rel="noopener noreferrer">
            <Icon src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" />
          </a>
        </IconsContainer>
        <ModelText>
          {ModelComponent ? <ModelComponent /> : "Информация о модели недоступна."}
        </ModelText>
        <CloseButton onClick={onClose}>Закрыть</CloseButton>
      </ModalContent>
    </ModalOverlay>
  );
};

export default ModalContact;
