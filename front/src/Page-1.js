import { Link as RouterLink } from 'react-router-dom';
import React from 'react';
import { Link as DSLink, Container } from '@dataesr/react-dsfr';

const Page1 = () => (
  <>
    <h2>Page 1</h2>
    <Container>
      <DSLink title="title" as={<RouterLink to="/page-2">Internal Link Page 2</RouterLink>} /></Container>
  </>
);
export default Page1;
