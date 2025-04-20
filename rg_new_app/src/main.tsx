import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomeScreen from './index';
import PrivacyPolicy from './privacy-policy';
import NotFound from './not-found';
import Layout from './_layout';
import './index.css';

const rootElement = document.getElementById('root')!;
ReactDOM.createRoot(rootElement).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Layout><HomeScreen /></Layout>} />
      <Route path="/privacy-policy" element={<Layout><PrivacyPolicy /></Layout>} />
      <Route path="*" element={<Layout><NotFound /></Layout>} />
    </Routes>
  </BrowserRouter>
);