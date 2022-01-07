import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import {
  Footer,
  FooterTopCategory,
  FooterLink,
  FooterTop,
  FooterBody,
  FooterBodyItem,
  FooterPartners,
  FooterPartnersTitle,
  FooterPartnersLogo,
  Logo,
  FooterBottom,
  FooterCopy,
  Link,
  SwitchTheme,
} from '@dataesr/react-dsfr';

const FooterExample = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Footer>
        <FooterBody
          description="Green Data For Health. Action Phare du PNES 4"
        >
          <Logo>Ministère de la Transition Ecologique et Solidaire</Logo>
          <FooterBodyItem>
            <Link href="https://legifrance.gouv.fr">
              legifrance.gouv.fr
            </Link>
          </FooterBodyItem>
          <FooterBodyItem>
            <Link href="https://gouvernement.fr">
              gouvernement.fr
            </Link>
          </FooterBodyItem>
          <FooterBodyItem>
            <Link href="https://service-public.fr">
              service-public.fr
            </Link>
          </FooterBodyItem>
          <FooterBodyItem>
            <Link href="https://data.gouv.fr">
              data.gouv.fr
            </Link>
          </FooterBodyItem>
        </FooterBody>
          
        <FooterBottom>
        <FooterCopy href="/">© République Française 2021 - Licence Ouverte Etalab</FooterCopy>
        </FooterBottom>
      </Footer>
      <SwitchTheme isOpen={isOpen} setIsOpen={setIsOpen} />
    </>
  );
};

export default FooterExample;
