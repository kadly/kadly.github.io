import React from 'react';
import styled from 'styled-components';

const ModalContact = ({ isOpen, onClose }) => {
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
          <a href="https://wa.me/79237082254" target="_blank" rel="noopener noreferrer">
            <Icon src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" />
          </a>
        </IconsContainer>
        <CloseButton onClick={onClose}>Закрыть</CloseButton>
      </ModalContent>
    </ModalOverlay>
  );
};

export default ModalContact;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ModalContent = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
`;

const IconsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
`;

const Icon = styled.img`
  width: 50px;
  height: 50px;
  transition: transform 0.3s ease;
  &:hover {
    transform: scale(1.1);
  }
`;

const CloseButton = styled.button`
  padding: 10px 20px;
  background: #333;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
  &:hover {
    background: #555;
  }
`;
