import React from "react";
import Slider from "react-slick";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import styled from "styled-components";

// Импортируем обязательные стили для слайдера
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const SliderWrapper = styled.div`
  width: 100%;
  max-width: 100vw; /* Жестко ограничиваем максимальную ширину размером экрана */
  overflow: hidden;

  .slick-slider,
  .slick-list,
  .slick-track {
    width: 100% !important; /* !important для переопределения инлайн-стилей JS */
  }

  .slick-slide > div {
    width: 100%;
  }

  .slick-prev:before,
  .slick-next:before {
    color: black; // Делаем стрелки видимыми на светлом фоне
  }
`;

const ImageSlider = ({ images }) => {
  const settings = {
    dots: false,
    arrows: false,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    adaptiveHeight: true,
    autoplay: true,
    autoplaySpeed: 3000,
  };

  return (
    <SliderWrapper>
      <Slider {...settings}>
        {images.map((imageNode, index) => {
          const image = getImage(imageNode.node);
          return (
            <div key={index}>
              <GatsbyImage image={image} alt={`Slide ${index + 1}`} />
            </div>
          );
        })}
      </Slider>
    </SliderWrapper>
  );
};

export default ImageSlider;
