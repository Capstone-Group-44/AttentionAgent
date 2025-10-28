import React, { useState } from 'react';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { getFirestore, doc, getDoc, setDoc } from 'firebase/firestore';
import { useNavigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const auth = getAuth();
  const db = getFirestore();
  const navigate = useNavigate();
  const [authing, setAuthing] = useState(false);

  const signInWithGoogle = async () => {
    setAuthing(true);
    try {
      const response = await signInWithPopup(auth, new GoogleAuthProvider());
      const user = response.user;

      // Check if a Firestore user doc already exists
      const userRef = doc(db, 'users', user.uid);
      const docSnap = await getDoc(userRef);

      if (!docSnap.exists()) {
        // Create user document for the first time
        await setDoc(userRef, {
          email: user.email,
          displayName: user.displayName || 'Anonymous',
          createdAt: new Date(),
        });
        console.log('New user document created:', user.uid);
      } else {
        console.log('User document already exists');
      }

      navigate('/focus', { replace: true }); 
    } catch (error) {
      console.error(error);
      setAuthing(false);
    }
  };

  return (
    <div>
      <p>Login Page</p>
      <button onClick={signInWithGoogle} disabled={authing}>
        Sign in with Google
      </button>
    </div>
  );
};

export default LoginPage;
