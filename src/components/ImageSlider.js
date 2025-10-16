import React from "react";
import Slider from "react-slick";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import styled from "styled-components";

// Импортируем обязательные стили для слайдера
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const SliderWrapper = styled.div`
  width: 100%;
  overflow: hidden; /* Финальная страховка от переполнения */

  .slick-slide > div {
    /* Заставляем контейнер слайда центрировать изображение */
    display: flex;
    justify-content: center;
  }

  .gatsby-image-wrapper {
    /* Заставляем изображение занимать 100% ширины контейнера */
    width: 100%;
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
