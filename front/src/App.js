import React from 'react';
import { Title } from '@dataesr/react-dsfr';
import Webpages from './webpages';
import {Home} from './Home';
import HeaderExample from './components/Header/Header'
const App = () => {

  return (
    <>
        
          <Webpages></Webpages>

        <HeaderExample/>
        <div>this is home page</div>
        </>  
        
  );
};

export default App;
