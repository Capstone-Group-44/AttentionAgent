import { doc, getDoc, setDoc } from "firebase/firestore";
import { db } from "../firebase";

export type UserProfile = {
  displayName: string;
  bio: string;
};

export async function saveUserProfile(uid: string, data: UserProfile) {
  await setDoc(doc(db, "users", uid), data, { merge: true });
}

export async function getUserProfile(uid: string): Promise<UserProfile | null> {
  const snapshot = await getDoc(doc(db, "users", uid));

  if (!snapshot.exists()) {
    return null;
  }

  const data = snapshot.data();

  return {
    displayName: data.displayName ?? "",
    bio: data.bio ?? "",
  };
}
