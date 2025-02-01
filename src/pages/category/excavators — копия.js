import React from "react";
import { Link } from "gatsby";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import { graphql, useStaticQuery } from "gatsby";
import styled from "styled-components";

const excavators = [
  "ZE60E-10", "ZE135E-10", "ZE155E-10", "ZE215E", "ZE245E", 
  "ZE330E-10", "ZE335", "ZE370E", "ZE490EK-10", "ZE550EK-10", 
  "ZE700ESP", "ZE730EK-10", "ZE960G", "ZE1250G", "ZE150WG"
];

const ExcavatorsPage = () => {
  return (
    <Layout>
    <>
      <Header>
        <h1>Экскаваторы</h1>
        <a href="https://cranetruck.ru">
        <h2>Zoomlion</h2>
        </a>
        <ContactInfo>
          <p>г. Новосибирск</p>
          <p>
            <ContactItem>
              <a href="tel:+7-923-708-22-54">+7-923-708-22-54</a>
            </ContactItem>
            <StyledLink href="https://t.me/gmitry">
              <TelegramLogo src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png" alt="Telegram logo"/>
            </StyledLink>
          </p>
        </ContactInfo>
      </Header>
      <Container>
        {/*<h2>Модели автокранов</h2>*/}
        <Grid>
          {excavators.map((model) => (
            <Card key={model}>
              <h3>{model}</h3>
            </Card>
          ))}
        </Grid>
      </Container>
      <Footer>
        <p>&copy; {new Date().getFullYear()} Краны и спецтехника. Все права защищены.</p>
      </Footer>
    </>
    </Layout>
  );
};

export default ExcavatorsPage;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #333;
  color: white;

  h1 {
    margin: 0;
    font-size: 24px;
  }

  a {
    text-decoration: none;
    color: black;
  }

  h2 {
    margin: 0;
    font-size: 56px;
    color: #006f3d;
    font-weight: bold;
    margin-left: 10px;
    text-shadow: 0 0 8px rgba(255, 255, 255, 0.6), 0 0 10px rgba(255, 255, 255, 0.5);
    -webkit-text-stroke: 1px #fff;
    letter-spacing: 2px;
    animation: fadeIn 1s ease-in-out;

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }
`;

const ContactInfo = styled.div`
  text-align: right;
  font-size: 20px;
  font-weight: bold;
  color: #00c851;
  text-shadow: 0 0 10px rgba(0, 200, 81, 0.7);
  letter-spacing: 1px;
  padding: 5px 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
    p {
    margin: 5px 0;
  }
`;

const Footer = styled.footer`
  text-align: center;
  padding: 20px;
  background: #333;
  color: white;
  //margin-top: auto;
`;

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  flex: 1; // Это заставит контейнер расти и занимать доступное пространство
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  background: #fff;
  padding: 16px;

  h3 {
    margin: 10px 0;
    font-size: 18px;
  }
`;

const TelegramLogo = styled.img`
  height: 40px;
  width: 40px;
  margin-left: 10px;
  vertical-align: middle;
  transition: transform 0.3s ease;
  &:hover {
    transform: scale(1.1);
  }
`;

const StyledLink = styled.a`
  text-decoration: none;
  display: inline-block;
  vertical-align: middle;
`;

const ContactItem = styled.span`
  & > a {
    transition: transform 0.3s ease, color 0.3s ease;
    display: inline-block;
    color: #00c851;

    &:hover {
      transform: scale(1.02);
    }
  }
`;

const Layout = styled.div`
  display: flex;
  min-height: 100vh;
  flex-direction: column;
`;