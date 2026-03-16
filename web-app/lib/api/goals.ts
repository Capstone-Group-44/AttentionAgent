import { doc, setDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export type UserGoals = {
  sessionsGoal: number;
  focusGoalSeconds: number;
  focusScoreGoal: number;
};

export const defaultGoals: UserGoals = {
  sessionsGoal: 6,
  focusGoalSeconds: 3600,
  focusScoreGoal: 95,
};

export async function saveUserGoals(uid: string, goals: UserGoals) {
  const ref = doc(db, "users", uid, "settings", "goals");

  await setDoc(
    ref,
    {
      sessionsGoal: goals.sessionsGoal,
      focusGoalSeconds: goals.focusGoalSeconds,
      focusScoreGoal: goals.focusScoreGoal,
    },
    { merge: true },
  );
}
