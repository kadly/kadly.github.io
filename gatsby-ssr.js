import React from 'react';

export const onRenderBody = ({ setPostBodyComponents }) => {
  setPostBodyComponents([
    <script
      key="goatcounter"
      data-goatcounter="https://kadly.goatcounter.com/count"
      async
      src="//gc.zgo.at/count.js"
    />,
  ]);
};