import { BrowserRouter, Route, Routes, Link, NavLink } from 'react-router-dom';

import Home from "./Home";
import DatasetList from "./DatasetList";
import OrganizationList from "./OrganizationList";
import Page1 from './Page-1';
import Page2 from './Page-2';

const Webpages = () => {
    return(
        <BrowserRouter>
        <Routes>
            
            <Route path = "/datasets" element= {<DatasetList />} />
            <Route path = "/organizations" element= {<OrganizationList />} />
            <Route exact path="/references" element={<Page1/>} />
            <Route exact path="/page-2" element={<Page2/>} />
        </Routes>
        </BrowserRouter>
    );
};

export default Webpages;
