"use client";

import { useState } from "react";
import { auth, db } from "@/lib/firebase";
import {
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "firebase/auth";
import { doc, getDoc, setDoc, getFirestore } from "firebase/firestore";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // GOOGLE LOGIN
  // -----------------------------
  async function loginWithGoogle() {
    setLoading(true);
    setError("");

    try {
      const provider = new GoogleAuthProvider();
      const res = await signInWithPopup(auth, provider);
      const user = res.user;

      const userRef = doc(db, "users", user.uid);
      const snap = await getDoc(userRef);

      if (!snap.exists()) {
        await setDoc(userRef, {
          email: user.email,
          displayName: user.displayName || "User",
          createdAt: new Date(),
        });
      }

      router.push("/");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  // Email + password login
  async function loginWithEmail(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  // Register new users
  async function register() {
    setLoading(true);
    setError("");

    try {
      const res = await createUserWithEmailAndPassword(auth, email, password);
      const user = res.user;

      const userRef = doc(db, "users", user.uid);
      await setDoc(userRef, {
        email: user.email,
        displayName: email.split("@")[0],
        createdAt: new Date(),
      });

      router.push("/");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-100">
      <div className="p-8 bg-white rounded-xl shadow w-full max-w-sm space-y-6">

        <h1 className="text-xl font-semibold text-center">
          Login
        </h1>

        {error && <p className="text-red-600 text-sm text-center">{error}</p>}

        {/* Email Login */}
        <form onSubmit={loginWithEmail} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Email</label>
            <input
              className="border p-2 rounded w-full"
              type="email"
              placeholder="you@example.com"
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
              placeholder="•••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-black text-white rounded hover:bg-gray-800"
          >
            {loading ? "Logging in..." : "Login with Email"}
          </button>
        </form>

        <button
          onClick={register}
          disabled={loading}
          className="w-full py-2 bg-gray-200 text-black rounded hover:bg-gray-300"
        >
          Create Account
        </button>

        {/* Google Login */}
        <button
          disabled={loading}
          onClick={loginWithGoogle}
          className="w-full py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          {loading ? "Signing in..." : "Sign in with Google"}
        </button>

      </div>
    </div>
  );
}
