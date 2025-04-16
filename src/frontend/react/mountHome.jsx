import React from 'react';
import { createRoot } from 'react-dom/client';
import Home from './components/Home';

const el = document.getElementById('home-root');
if (el) {
  const root = createRoot(el);
  root.render(<Home />);
}
