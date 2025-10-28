import './App.css'
import { initializeApp } from 'firebase/app';
import { config } from './config/config';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthRoute from './components/AuthRoute';
import HomePage from './pages/Home';
import LoginPage from './pages/Login';
import FocusPage from './pages/Focus';


initializeApp(config.firebaseConfig);

function App() {
  return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route
                    path="/"
                    element={
                        <AuthRoute>
                            <HomePage />
                        </AuthRoute>
                    }
                />
                <Route
                    path="/focus"
                    element={
                        <AuthRoute>
                            <FocusPage />
                        </AuthRoute>
                    }
                />
                {/* Public route */}
                <Route path="/login" element={<LoginPage />} />

            </Routes>
        </BrowserRouter>
    );
}

export default App
