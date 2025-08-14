import React from "react";
import { Link } from "gatsby";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import { graphql, useStaticQuery } from "gatsby";
import styled from "styled-components";
import Footer from "../components/Footer";
import YandexMap from "../components/YandexMap";

const categories = [
  { name: "Автокраны", image: "autocranes.png", description: "Мобильные краны для строительства.", path: "/category/autocranes" },
  { name: "Автокраны полноприводные", image: "all-terrain-cranes.png", description: "Краны для работы в сложных условиях.", path: "/category/allterraincranes" },
  { name: "Краны короткобазные", image: "short-base-cranes.png", description: "Компактные краны для узких пространств.", path: "/category/shortbasecranes" },
  { name: "Краны гусеничные", image: "crawler-cranes.png", description: "Гусеничные краны для тяжелых работ.", path: "/category/crawlercranes" },
  { name: "Краны гусеничные с телескопической стрелой", image: "telescopic-crawler-cranes.png", description: "Гибкие решения для строительства.", path: "/category/telescopiccrawlercranes" },
  { name: "Манипуляторы", image: "manipulators.png", description: "Многофункциональные манипуляторы.", path: "/category/manipulators" },
  { name: "Минипогрузчики", image: "skid-steer-loaders.png", description: "Компактные погрузчики для небольших задач.", path: "/category/skidsteerloaders" },
  { name: "Экскаваторы", image: "excavators.png", description: "Экскаваторы для копательных работ.", path: "/category/excavators" },
  { name: "Экскаватор грейферный", image: "clamshell-excavators.png", description: "Грейферные экскаваторы для точных операций.", path: "/category/clamshellexcavators" },
  { name: "Бульдозеры", image: "bulldozers.png", description: "Тяжелая техника для землеройных работ.", path: "/category/bulldozers" },
  { name: "Фронтальные погрузчики", image: "front-end-loaders.png", description: "Погрузчики для перемещения материалов.", path: "/category/frontendloaders" },
];

const IndexPage = () => {
  const data = useStaticQuery(graphql`
    query {
      allFile(filter: {sourceInstanceName: {eq: "images"}}) {
        nodes {
          base
          childImageSharp {
            gatsbyImageData(width: 300, placeholder: BLURRED, formats: [AUTO, WEBP])
          }
        }
      }
    }
  `);

  const getImageByName = (name) => {
    const match = data.allFile.nodes.find(({ base }) => base === name);
    return match ? getImage(match.childImageSharp) : null;
  };

  return (
    <>
      <Header>
        <h1>Краны и спецтехника</h1>
        <h2>Zoomlion</h2>
        <ContactInfo>
          <p>г. Новосибирск</p>
          <p>
            <ContactItem>
              <a href="tel:+7-923-708-22-54">+7-923-708-22-54</a>
            </ContactItem>
            <StyledLink href="https://t.me/gmitry">
              <TelegramLogo src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png" alt="Telegram logo" />
            </StyledLink>
            <StyledLink href="https://wa.me/79237082254" target="_blank" rel="noopener noreferrer">
              <WhatsappLogo src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/512px-WhatsApp.svg.png" alt="WhatsApp logo" />
            </StyledLink>
          </p>
        </ContactInfo>
      </Header>
      <Container>
        <Grid>
          {categories.map((category) => (
            <Card key={category.name}>
              <Link to={category.path}>
                <ImageWrapper>
                  {getImageByName(category.image) ? (
                    <GatsbyImage image={getImageByName(category.image)} alt={category.name} />
                  ) : (
                    <Placeholder>No Image</Placeholder>
                  )}
                </ImageWrapper>
                <h3>{category.name}</h3>
                <p>{category.description}</p>
              </Link>
            </Card>
          ))}
        </Grid>
      </Container>
      <YandexMap />
      <Footer
        companyName="Зумлион Индустри"
        websiteUrl="https://example.com"
      />
    </>
  );
};

export default IndexPage;

const Header = styled.header`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: linear-gradient(to right, #333 85%, #666);
  color: white;

  h1 {
    margin: 0;
    font-size: 24px;

    @media (max-width: 480px) {
      font-size: 20px;
    }
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
    letter-spacing: 2px;
    text-shadow: 
      -1px -1px 0 #fff,
       1px -1px 0 #fff,
      -1px  1px 0 #fff,
       1px  1px 0 #fff,
       0 0 8px rgba(255, 255, 255, 0.6),
       0 0 10px rgba(255, 255, 255, 0.5);
    animation: fadeIn 1s ease-in-out;
  
    @media (max-width: 480px) {
      font-size: 32px;
    }
  
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

  @media (max-width: 480px) {
    flex-direction: column;
    text-align: center;
  }
`;

const ContactInfo = styled.div`
  text-align: right;
  font-size: 20px;
  color: #00c851;
  text-shadow: 0 0 10px rgba(0, 200, 81, 0.7);
  letter-spacing: 1px;
  padding: 5px 15px;
  border-radius: 8px;

  p {
    margin: 5px 0;
  }

  /* Для мобильных устройств (<480px) */
  @media (max-width: 480px) {
    text-align: center;
  }

  /* Для планшетов: город и телефон с логотипом Telegram в одну строку, центрирование */
  @media (min-width: 481px) and (max-width: 768px) {
    display: flex;
    align-items: center;
    justify-content: center;
    p {
      margin: 0 10px;
    }
  }
`;

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
`;

const Grid = styled.div`
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  background: #fff;

  a {
    text-decoration: none;
    color: inherit;
    display: block;
    padding: 16px;
  }

  h3 {
    margin: 10px 0;
    font-size: 18px;
  }

  p {
    font-size: 14px;
    color: #555;
  }
`;

const ImageWrapper = styled.div`
  height: 200px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  overflow: hidden;
`;

const Placeholder = styled.div`
  width: 100%;
  height: 100%;
  background: #eee;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  color: #888;
  font-size: 14px;
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

const WhatsappLogo = styled.img`
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
    font-weight: bold;
    transition: transform 0.3s ease, color 0.3s ease;
    display: inline-block;
    color: #00c851;

    &:hover {
      transform: scale(1.02);
    }
  }
`;