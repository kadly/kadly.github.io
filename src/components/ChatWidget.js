import React, { useState, useRef, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

// Keyframes for animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
`;

// Styled Components
const ChatWidgetContainer = styled.div`
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
`;

const ChatBubble = styled.button`
  background-color: #0088cc;
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }
`;

const ChatWindow = styled.div`
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 370px;
  height: 500px;
  background-color: #e9e9e9;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ${fadeIn} 0.3s ease-out;

  @media (max-width: 480px) {
    width: 100%;
    height: 100%;
    right: 0;
    bottom: 0;
    border-radius: 0;
  }
`;

const ChatHeader = styled.div`
  background-color: #0088cc;
  color: white;
  padding: 0 15px;
  font-weight: bold;
  position: relative; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  height: 50px; 
`;

const CloseButton = styled.button`
  position: absolute;
  top: 50%;
  right: 15px;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  line-height: 1;
  padding: 0;
  cursor: pointer;
  font-weight: bold;

  &:hover {
    opacity: 0.8;
  }
`;

const MessageList = styled.div`
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const Message = styled.div`
  margin-bottom: 15px;
  padding: 10px 15px;
  border-radius: 20px;
  max-width: 80%;
  align-self: ${props => (props.sender === 'user' ? 'flex-end' : 'flex-start')};
  background-color: ${props => (props.sender === 'user' ? '#dcf8c6' : '#ffffff')};
  animation: ${fadeIn} 0.4s ease;
`;

const InputArea = styled.form`
  display: flex;
  padding: 10px;
  background-color: #f0f0f0;
  border-top: 1px solid #ddd;
`;

const TextInput = styled.input`
  flex-grow: 1;
  border: none;
  padding: 10px;
  border-radius: 20px;
  background-color: white;
  &:focus {
    outline: none;
  }
`;

const SendButton = styled.button`
  background-color: #0088cc;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  margin-left: 10px;
  cursor: pointer;
  font-size: 20px;
`;

const TypingIndicator = styled.div`
    align-self: flex-start;
    color: #888;
    font-style: italic;
`;

// The Component
const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: 'Здравствуйте! Чем могу помочь?', sender: 'bot' },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messageListRef = useRef(null);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = { text: inputValue, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });

      if (!res.ok) {
        throw new Error('API Error');
      }

      const data = await res.json();
      const botMessage = { text: data.reply, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = { text: 'Ошибка. Попробуйте еще раз.', sender: 'bot' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatWidgetContainer>
      {isOpen && (
        <ChatWindow>
                    <ChatHeader>
            ИИ-Помощник
            <CloseButton onClick={() => setIsOpen(false)}>&times;</CloseButton>
          </ChatHeader>
          <MessageList ref={messageListRef}>
            {messages.map((msg, index) => (
              <Message key={index} sender={msg.sender}>
                {msg.text}
              </Message>
            ))}
            {isLoading && <TypingIndicator>Печатает...</TypingIndicator>}
          </MessageList>
          <InputArea onSubmit={handleSubmit}>
            <TextInput
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Спросите что-нибудь..."
            />
            <SendButton type="submit">➤</SendButton>
          </InputArea>
        </ChatWindow>
      )}
      {!isOpen && (
        <ChatBubble onClick={() => setIsOpen(true)}>
          {'💬'}
        </ChatBubble>
      )}
    </ChatWidgetContainer>
  );
};

export default ChatWidget;
