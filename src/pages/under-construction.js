import React from "react";
import { Link } from "gatsby";
import styled from "styled-components";

const PageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
`;

const Title = styled.h1`
  font-size: 48px;
  margin-bottom: 20px;
`;

const Message = styled.p`
  font-size: 24px;
  margin-bottom: 40px;
`;

const BackLink = styled(Link)`
  font-size: 20px;
  color: #0088cc;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;

const UnderConstructionPage = () => {
  return (
    <PageWrapper>
      <Title>🚧</Title>
      <Message>Страница находится в разработке</Message>
      <BackLink to="/">Вернуться на главную</BackLink>
    </PageWrapper>
  );
};

export default UnderConstructionPage;
