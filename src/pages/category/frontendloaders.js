import React, { useState } from 'react';
import { graphql } from 'gatsby';
import ModalContact from '../../components/ModalContact';
import ModelCard from '../../components/ModelCard';
import Header, { Head as HeaderHead } from '../../components/Header';
import Footer from '../../components/Footer';
import { Layout, Container, Grid, Subtitle } from '../../components/LayoutComponents';

const FrontendloadersPage = ({ data }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);

  const handleCardClick = (model) => {
    setSelectedModel(model);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedModel(null);
  };

  const images = data.images.edges;
  const models = data.models.edges.map(edge => edge.node);

  const getModelImage = (modelId) => {
    const imageNode = images.find(edge => edge.node.name === modelId);
    return imageNode ? imageNode.node.childImageSharp.gatsbyImageData : null;
  };

  const ModelDetails = ({ details }) => (
    <div>
      <ul>
        {details.map(detail => (
          <li key={detail.label}>
            <strong>{detail.label}:</strong> {detail.value}
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <Layout>
      <Header centerText="Фронтальные погрузчики" />

      <Container>
        <Grid>
          {models.map((model) => (
            <ModelCard
              key={model.modelId}
              name={model.name}
              imageData={getModelImage(model.modelId)}
              onClick={() => handleCardClick(model)}
            />
          ))}
        </Grid>
      </Container>

      <ModalContact
        isOpen={isModalOpen}
        onClose={closeModal}
        ModelComponent={selectedModel ? () => <ModelDetails details={selectedModel.details} /> : null}
      >
        {selectedModel && <Subtitle>{selectedModel.name}</Subtitle>}
      </ModalContact>

      <Footer
        companyName="Зумлион Индустри"
        yearsActive="25"
        websiteUrl="https://example.com"
      />
    </Layout>
  );
};

export const query = graphql`
  query {
    images: allFile(filter: { relativeDirectory: { eq: "frontendloaders" } }) {
      edges {
        node {
          name
          childImageSharp {
            gatsbyImageData(width: 300, layout: CONSTRAINED)
          }
        }
      }
    }
    models: allFrontendloadersJson {
      edges {
        node {
          modelId
          name
          details {
            label
            value
          }
        }
      }
    }
  }
`;

export default FrontendloadersPage;

export const Head = HeaderHead;