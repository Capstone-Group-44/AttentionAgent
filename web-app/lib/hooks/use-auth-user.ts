"use client";

import { useEffect, useState } from "react";
import { onAuthStateChanged, type User } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";
import { auth, db } from "@/lib/firebase";

type AppUser = User & {
  role?: "admin" | "user";
  displayName?: string | null;
};

export function useAuthUser() {
  const [user, setUser] = useState<AppUser | null>(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (u) => {
      if (!u) {
        setUser(null);
        setAuthReady(true);
        return;
      }

      const ref = doc(db, "users", u.uid);
      const snap = await getDoc(ref);

      const extraData = snap.exists() ? snap.data() : {};

      setUser({
        ...u,
        ...extraData,
      });

      setAuthReady(true);
    });

    return () => unsub();
  }, []);

  return { user, authReady };
}
