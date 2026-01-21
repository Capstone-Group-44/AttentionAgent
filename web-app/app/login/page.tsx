"use client";

import { useEffect, useState } from "react";
import { auth, db } from "@/lib/firebase";
import {
  GoogleAuthProvider,
  signInWithRedirect,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  setPersistence,
  signInWithPopup,
  browserSessionPersistence,
} from "firebase/auth";
import { doc, getDoc, setDoc, serverTimestamp } from "firebase/firestore";
import { useRouter } from "next/navigation";
import Link from "next/link";

type FirebaseUserSnapshot = {
  uid: string;
  email: string | null;
  displayName: string | null;
};

const DESKTOP_CALLBACK_PORT =
  process.env.NEXT_PUBLIC_DESKTOP_CALLBACK_PORT ?? "5000";
const DESKTOP_CALLBACK_URL = `http://127.0.0.1:${DESKTOP_CALLBACK_PORT}`;

async function notifyDesktop(user: FirebaseUserSnapshot | null) {
  if (!user || !user.uid) {
    return;
  }

  const email = user.email ?? "";
  if (!email) {
    console.warn("Desktop callback skipped because email was missing");
    return;
  }

  const name = user.displayName || email.split("@")[0] || "User";
  const payload = {
    name,
    email,
    uid: user.uid,
    display_name: user.displayName || name,
    created_at: new Date().toISOString(),
  };

  try {
    await fetch(`${DESKTOP_CALLBACK_URL}/callback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.warn("Desktop login callback failed", error);
  }
}

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [emailLoading, setEmailLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  
  const [error, setError] = useState("");

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (user) => {
      if (!user) return;

      try {
        //setLoading(true);

        // Create /users/{uid} if it doesn't exist
        const userRef = doc(db, "users", user.uid);
        const snap = await getDoc(userRef);

        if (!snap.exists()) {
          await setDoc(userRef, {
            email: user.email,
            displayName: user.displayName || user.email?.split("@")[0] || "User",
            createdAt: serverTimestamp(),
          });
        }

        await notifyDesktop(user);

        router.push("/");
      } catch (e: any) {
        setError(e?.message ?? "Failed to finish login.");
      } finally {
        setEmailLoading(false);
        setGoogleLoading(false);
      }
    });

    return () => unsub();
  }, [router]);


async function loginWithGoogle() {
  setGoogleLoading(true);
  setError("");

  try {
    await setPersistence(auth, browserSessionPersistence); // good for incognito
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
  } catch (err: any) {
    setError(err?.message ?? "Google sign-in failed.");
  } finally {
    setGoogleLoading(false);
  }
}
  async function loginWithEmail(e: React.FormEvent) {
    e.preventDefault();
    setEmailLoading(true);
    setError("");

    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      await notifyDesktop(credential.user);
      router.push("/");
    } catch (err: any) {
      setError(err?.message ?? "Email sign-in failed.");
      setEmailLoading(false);
    }
  }

  return (
    <div className="flex pt-10 items-center justify-center">
      <div className="p-8 bg-white rounded-xl shadow w-full max-w-sm space-y-6">
        <h1 className="text-xl font-semibold text-center">Login</h1>

        {error && <p className="text-red-600 text-sm text-center">{error}</p>}

        <form onSubmit={loginWithEmail} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Email</label>
            <input
              className="border p-2 rounded w-full"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium">Password</label>
            <input
              className="border p-2 rounded w-full"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={emailLoading || googleLoading}
            className="w-full py-2 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-60"
          >
            {emailLoading ? "Logging in..." : "Login with Email"}
          </button>
        </form>

        <button
          disabled={googleLoading || emailLoading}
          onClick={loginWithGoogle}
          className="w-full py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-60"
        >
          {googleLoading ? "Signing in..." : "Sign in with Google"}
        </button>
        
        <div className="text-center text-sm">
            New to Focus Cam? {" "}
            <Link href="/register" className="text-blue-600 hover:underline">
              Register here
            </Link>
          </div>
      </div>
    </div>
  );
}
