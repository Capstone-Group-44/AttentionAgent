"use client";

import { useState } from "react";
import { auth } from "@/lib/firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc, getFirestore } from "firebase/firestore";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const db = getFirestore();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function register(e: React.FormEvent) {
    e.preventDefault();
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

      // Redirect to login page after successful registration
      router.push("/login");
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="flex pt-10 items-center justify-center">
      <div className="p-8 bg-white rounded-xl shadow w-full max-w-sm space-y-4">
        <h1 className="text-xl font-semibold text-center">Create Account</h1>

        {error && <p className="text-red-600 text-sm text-center">{error}</p>}

        <form onSubmit={register} className="space-y-4">
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
            {loading ? "Creating Account..." : "Register"}
          </button>
        </form>

        <div className="text-center text-sm">
          <p>
            Already have an account?{" "}
            <Link href="/login" className="text-blue-600 hover:underline">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
