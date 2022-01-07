import React, { useEffect, useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
// import ChangeLang from '../components/Toggle/Toggle';
import {
  Header,
  HeaderOperator,
  HeaderBody,
  Logo,
  Service,
  Tool,
  ToolItem,
  ToolItemGroup,
  HeaderNav,
  NavItem,
  NavSubItem,
  MegaNavSubItem,
  MegaNavItem,
  Link,
  SwitchTheme,
  // Toggle,
  useTheme,
} from '@dataesr/react-dsfr';

// import Logo from '@gouvfr/dsfr'

// import logo from './culture-logo.png'

const MyHeader = () => {
  const location = useLocation();
  const theme = useTheme();
  const [path, setPath] = useState(() => location.pathname || '');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (path !== location.pathname) {
      setPath(location.pathname);
    }
  }, [path, setPath, location]);

  return (
    <>
      <Header>
        <HeaderBody>
          <HeaderOperator>
          <Logo splitCharacter={10}>Ministère de la Transition Ecologique</Logo>
          </HeaderOperator> 
          <Service
            asLink={<RouterLink to="/" />}
            title="Green Data For Health"
            description="Portail de jeux de données en Santé-Environnement"
          />
          <Tool
            closeButtonLabel="fermer"
          >
            <ToolItemGroup>
              
            {/* <ToolItem>
              <ChangeLang/>
              </ToolItem>
              <ToolItem onClick={() => setIsOpen(true)}>
                <span
                  className="fr-fi-theme-fill fr-link--icon-left"
                  aria-controls="fr-theme-modal"
                  data-fr-opened={isOpen}
                >
                  Paramètres d’affichage
                </span>
              </ToolItem> */}
            </ToolItemGroup>
            
          </Tool>
        </HeaderBody>
        <HeaderNav path={path}>
          <NavItem title="A propos" link="/"
          current={path}
          asLink={<RouterLink to="/" />}>
          </NavItem>
          <NavItem title="Jeux de données" link="/datasets"
            current={path.startsWith('/datatets')}
            asLink={<RouterLink to="/datasets" />}
          />

          <NavItem
            title="Organismes"
            current={path.startsWith('/organizations')}
            asLink={<RouterLink to="/organizations" />}
          />
          
          <NavItem title="Référentiels">
            <NavSubItem
              current={path.startsWith('/references')}
              title="Référentiels controlés"
              asLink={<RouterLink to="/references#controled" />}
            />
            <NavSubItem
              current={path.startsWith('/references')}
              asLink={<RouterLink to="/references#free" />}
              title="Référentiels libres "
            />
            
          </NavItem>
          <MegaNavItem
            title="Contribuer"
            description="Proposez un jeu de données"
            as="h3"
            closeButtonLabel="Fermeture"
            linkLabel="Participer au GD4H"
            link="/"
          >
          </MegaNavItem>
        </HeaderNav>
      </Header>
      
    </>
  );
};

export default MyHeader;
