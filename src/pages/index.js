import React, { useEffect } from "react";
import { Link } from "gatsby";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import { graphql, useStaticQuery } from "gatsby";
import styled, { keyframes } from "styled-components";
import Footer from "../components/Footer";
import YandexMap from "../components/YandexMap";
import ImageSlider from "../components/ImageSlider";

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

const TelegramWidget = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.async = true;
    script.setAttribute('data-telegram-post', 'zoomlionsu/4');
    script.setAttribute('data-width', '100%');

    const widgetContainer = document.getElementById('telegram-widget-container');
    if (widgetContainer) {
      widgetContainer.innerHTML = '';
      widgetContainer.appendChild(script);
    }

    return () => {
      if (widgetContainer && widgetContainer.contains(script)) {
        widgetContainer.removeChild(script);
      }
    };
  }, []);

  return <div id="telegram-widget-container"></div>;
};

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
      galleryImages: allFile(
        filter: {
          sourceInstanceName: { eq: "images" }
          relativeDirectory: { eq: "gallery" }
        }
      ) {
        edges {
          node {
            childImageSharp {
              gatsbyImageData(layout: CONSTRAINED, width: 800)
            }
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
          <p>
            <StyledLink href="https://t.me/gmitry">
              <TelegramLogo src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png" alt="Telegram logo" />
            </StyledLink>
            <StyledLink href="https://wa.me/79133777508" target="_blank" rel="noopener noreferrer">
              <WhatsappLogo src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/512px-WhatsApp.svg.png" alt="WhatsApp logo" />
            </StyledLink>
            <span style={{ marginLeft: '15px', verticalAlign: 'middle' }}>г. Новосибирск</span>
          </p>
        </ContactInfo>
      </Header>
      
      <PageLayout>
        <LeftSidebar>
          <h3>Услуги</h3>
          <ServiceMenu>
            <li><Link to="/under-construction/">Сервисное обслуживание</Link></li>
            <li><Link to="/under-construction/">Аренда</Link></li>
            <li><Link to="/under-construction/">Лизинг</Link></li>
            <li><Link to="/under-construction/">Доставка</Link></li>
          </ServiceMenu>
          <CarouselContainer>
            <h3>Фото площадки</h3>
            <ImageSlider images={data.galleryImages.edges} />
          </CarouselContainer>
        </LeftSidebar>

        <MainContent>
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
        </MainContent>

        <RightSidebar>
          <ContactsBlock>
            <h3>Контакты</h3>
            <ContactList>
              <li><a href="tel:+7-383-380-71-28">+7-383-380-71-28</a></li>
              <li><a href="tel:+7-913-377-75-08">+7-913-377-75-08</a></li>
              <li><a href="mailto:zoomlionsib@yandex.ru">zoomlionsib@yandex.ru</a></li>
            </ContactList>
          </ContactsBlock>
          <h3>Новости из Telegram</h3>
          <TelegramWidget />
        </RightSidebar>

        <MapContainer>
          <h3>Местоположение</h3>
          <YandexMap />
        </MapContainer>

      </PageLayout>

      <Footer
        companyName="Зумлион Индустри"
        websiteUrl="https://example.com"
      />
    </>
  );
};

export default IndexPage;

// --- Стили ---

const CarouselContainer = styled.div`
  margin-top: 20px;
  
  @media (max-width: 1200px) {
    order: 2; // На мобильных устройствах отправляем карусель вниз
    width: 100%;
    max-width: 500px;
    margin: 20px auto 0;
  }
`;

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const PageLayout = styled.div`
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-areas:
    "left main right"
    ". map .";
  gap: 30px;
  padding: 20px;
  max-width: 1800px;
  margin: 0 auto;
  align-items: flex-start;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-areas:
      "main"
      "left" // Эта область теперь будет содержать и меню, и карусель
      "right"
      "map";
    gap: 15px;
    padding: 20px 20px 10px 20px;
  }
`;

const MainContent = styled.main`
  grid-area: main;
`;

const LeftSidebar = styled.aside`
  grid-area: left;
  width: 280px;

  @media (max-width: 1200px) {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  h3 {
    text-align: center;
    margin-top: 0;
  }
`;

const ContactsBlock = styled.div`
  margin-bottom: 30px;
`;

const ContactList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;

  li {
    padding: 8px 0;
    border-bottom: 1px solid #ddd;
    font-size: 16px;
    &:first-child {
      border-top: 1px solid #ddd;
    }
  }

  a {
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: rgb(164, 206, 78);
    }
  }
`;

const RightSidebar = styled.aside`
  grid-area: right;
  width: 320px;
  h3 {
    text-align: center;
    margin-top: 0;
  }
  @media (max-width: 1200px) {
    width: 100%;
    max-width: 500px;
    margin: 20px auto 0; // Убираем нижний отступ
  }
`;

const MapContainer = styled.div`
  grid-area: map;
  h3 {
    text-align: center;
  }
`;

const ServiceMenu = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;

  li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
    &:last-child {
      border-bottom: none;
    }
  }

  a {
    text-decoration: none;
    color: inherit;
    display: block;
    transition: color 0.2s ease-in-out;

    &:hover {
      color: rgb(164, 206, 78);
    }
  }
`;

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
    animation: ${fadeIn} 1s ease-in-out;
  
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

  @media (max-width: 480px) {
    text-align: center;
  }

  @media (min-width: 481px) and (max-width: 768px) {
    display: flex;
    align-items: center;
    justify-content: center;
    p {
      margin: 0 10px;
    }
  }
`;

const Grid = styled.div`
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
