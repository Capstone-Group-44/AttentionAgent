"use client";

import { doc, onSnapshot } from "firebase/firestore";
import { useEffect, useState } from "react";
import { db } from "@/lib/firebase";
import { defaultGoals, type UserGoals } from "@/lib/api/goals";

export function useUserGoals(uid?: string) {
  const [goals, setGoals] = useState<UserGoals>(defaultGoals);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!uid) {
      setGoals(defaultGoals);
      setLoading(false);
      return;
    }

    const ref = doc(db, "users", uid, "settings", "goals");

    const unsubscribe = onSnapshot(
      ref,
      (snapshot) => {
        if (!snapshot.exists()) {
          setGoals(defaultGoals);
          setLoading(false);
          return;
        }

        const data = snapshot.data();

        setGoals({
          sessionsGoal: data.sessionsGoal ?? defaultGoals.sessionsGoal,
          focusGoalSeconds:
            data.focusGoalSeconds ?? defaultGoals.focusGoalSeconds,
          focusScoreGoal: data.focusScoreGoal ?? defaultGoals.focusScoreGoal,
        });

        setLoading(false);
      },
      (error) => {
        console.error("Failed to fetch user goals:", error);
        setGoals(defaultGoals);
        setLoading(false);
      },
    );

    return () => unsubscribe();
  }, [uid]);

  return { goals, loading };
}
