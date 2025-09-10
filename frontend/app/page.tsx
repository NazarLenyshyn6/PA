'use client';

import { useEffect } from 'react';
import LoginPage from './login/page';

export default function Home() {
  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      window.location.href = '/chat';
    }
  }, []);

  return <LoginPage />
}