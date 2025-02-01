import React from "react";
import { Link } from "gatsby";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import { graphql, useStaticQuery } from "gatsby";
import styled from "styled-components";

const categories = [
  { name: "Автокраны", image: "autocranes.png", description: "Мобильные краны для строительства.", path: "/category/autocranes" },
  { name: "Автокраны полноприводные", image: "all-terrain-cranes.png", description: "Краны для работы в сложных условиях.", path: "/category/all-terrain-cranes" },
  { name: "Краны короткобазные", image: "short-base-cranes.png", description: "Компактные краны для узких пространств.", path: "/category/short-base-cranes" },
  { name: "Краны гусеничные", image: "crawler-cranes.png", description: "Гусеничные краны для тяжелых работ.", path: "/category/crawler-cranes" },
  { name: "Краны гусеничные с телескопической стрелой", image: "telescopic-crawler-cranes.png", description: "Гибкие решения для строительства.", path: "/category/telescopic-crawler-cranes" },
  { name: "Манипуляторы", image: "manipulators.png", description: "Многофункциональные манипуляторы.", path: "/category/manipulators" },
  { name: "Минипогрузчики", image: "skid-steer-loaders.png", description: "Компактные погрузчики для небольших задач.", path: "/category/skid-steer-loaders" },
  { name: "Экскаваторы", image: "excavators.png", description: "Экскаваторы для копательных работ.", path: "/category/excavators" },
  { name: "Экскаватор грейферный", image: "clamshell-excavators.png", description: "Грейферные экскаваторы для точных операций.", path: "/category/clamshell-excavators" },
  { name: "Бульдозеры", image: "bulldozers.png", description: "Тяжелая техника для землеройных работ.", path: "/category/bulldozers" },
  { name: "Фронтальные погрузчики", image: "front-end-loaders.png", description: "Погрузчики для перемещения материалов.", path: "/category/front-end-loaders" },
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
          <p>+7-923-708-22-54</p>
        </ContactInfo>
      </Header>
      <Container>
        {/*<h2>Каталог техники</h2>*/}
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
      <Footer>
        <p>&copy; {new Date().getFullYear()} Краны и спецтехника. Все права защищены.</p>
      </Footer>
    </>
  );
};

export default IndexPage;

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
`;

const ContactInfo = styled.div`
  text-align: right;
  font-size: 14px;
`;

const Footer = styled.footer`
  text-align: center;
  padding: 20px;
  background: #333;
  color: white;
  margin-top: 40px;
`;

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
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
  align-items: center;
  justify-content: center;
  overflow: hidden;
`;

const Placeholder = styled.div`
  width: 100%;
  height: 100%;
  background: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-size: 14px;
`;
