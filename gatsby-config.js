module.exports = {
  siteMetadata: {
    title: "Краны и спецтехника",
    description: "Каталог специализированной техники в Новосибирске.",
    author: "@yourname",
  },
  plugins: [
    `gatsby-plugin-image`,
    `gatsby-plugin-sharp`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-styled-components`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
  ],
};