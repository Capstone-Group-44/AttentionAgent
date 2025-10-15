import React from 'react';
import { getAuth, signOut } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';

export interface IHomePageProps {}

const HomePage: React.FunctionComponent<IHomePageProps> = () => {
    const auth = getAuth();
    const navigate = useNavigate();

    return (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
      <h1>Welcome to FocusCam 👋</h1>
      <p>This is the home page.</p>
      <button onClick={() => navigate('/login')}>Login</button>

      {/* Optional: sign out if user is already logged in */}
      <button style={{ marginLeft: '1rem' }} onClick={() => signOut(auth)}>
        Sign Out
      </button>
    </div>
    );
};

export default HomePage;
