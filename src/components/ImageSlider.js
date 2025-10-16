import React, { useState, useEffect } from "react";
import Slider from "react-slick";
import { GatsbyImage, getImage } from "gatsby-plugin-image";
import styled from "styled-components";

// Импортируем обязательные стили для слайдера
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const SliderWrapper = styled.div`
  width: 100%;
  opacity: ${props => (props.visible ? 1 : 0)};
  transition: opacity 300ms ease-in-out;

  .gatsby-image-wrapper {
    width: 100%;
  }
`;

const ImageSlider = ({ images }) => {
  const [isSliderVisible, setIsSliderVisible] = useState(false);

  useEffect(() => {
    // Используем setTimeout с задержкой 0, чтобы этот код выполнился
    // после того, как основной поток рендеринга завершится.
    // Это дает карусели время для правильного расчета ширины.
    const timer = setTimeout(() => {
      setIsSliderVisible(true);
    }, 0);

    return () => clearTimeout(timer);
  }, []); // Пустой массив зависимостей означает, что эффект выполнится один раз

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
    <SliderWrapper visible={isSliderVisible}>
      {isSliderVisible && (
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
      )}
    </SliderWrapper>
  );
};

export default ImageSlider;