import React, { useState } from 'react';
import { Link } from "gatsby";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import { graphql, useStaticQuery } from "gatsby";
import styled from "styled-components";
import ModalContact from '../../components/ModalContact';

const autocranes = [
  "ZMC-25-1С", "ZMC-25-1С 6 (6х6)", "ZMC-60-1W1", "ZTC250V", "ZTC300V",
  "ZTC600V552.1T", "ZTC600V552.2C", "ZTC800V", "ZTC800V552.5C", "ZTC1000V",
  "ZTC1500H", "ZTC800V552.1T", "ZTC1000V", "ZTC1500H", "ZAT2000V",  
  "ZAT2500V", "ZAT3000V без суперлифта", "ZAT3000V с суперлифтом", 
  "ZAT3500V без суперлифта", "ZAT3500V с суперлифтом", "ZAT4500V без суперлифта", 
  "ZAT4500V с суперлифтом", "ZTC250V552-1T", "ZTC250V552-1C", 
  "ZTC300V552-1T", "ZTC300V552-1C", "ZTC500V552-1T", 
  "ZTC500V552-1C", "ZTC700V552-1T", "ZTC700V552-1C", 
  "ZTC800V552-1T", "ZTC800V552-1C", "ZAT1200V753.1T", 
  "ZAT1200V753.1C", "ZAT1600H853C", "ZAT2000V853C"
];

const AutocranesPage = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCardClick = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const images = useStaticQuery(graphql`
    query {
      allFile(filter: { relativeDirectory: { eq: "autocranes" } }) {
        edges {
          node {
            name
            childImageSharp {
              gatsbyImageData(width: 300, layout: CONSTRAINED)
            }
          }
        }
      }
    }
  `);

  const getModelImage = (model) => {
    const imageNode = images.allFile.edges.find(edge => edge.node.name === model);
    return imageNode ? getImage(imageNode.node.childImageSharp) : null;
  };

  return (
    <Layout>
      <Header>
        <h1>Автокраны</h1>
        <Link to="/">
          <h2>Zoomlion</h2>
        </Link>
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
        <Grid>
          {autocranes.map((model) => (
            <Card key={model} onClick={handleCardClick}>
              {getModelImage(model) ? (
                <GatsbyImage image={getModelImage(model)} alt={model} />
              ) : (
                <p>Нет фото</p>
              )}
              <h3>{model}</h3>
            </Card>
          ))}
        </Grid>
      </Container>
      <ModalContact isOpen={isModalOpen} onClose={closeModal} />
      <Footer>
        <p>&copy; {new Date().getFullYear()} Зумлион индустри. 25 лет на рынке в мире</p>
      </Footer>
    </Layout>
  );
};

export default AutocranesPage;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(to right, #333 85%, #666);
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
  margin-top: auto;
`;

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  flex: 1 0 auto;
`;

const Grid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
`;

const Card = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  background: #fff;
  padding: 16px;
  flex: 1 1 calc(33.333% - 20px);
  cursor: pointer;

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
