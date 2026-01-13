import {
  Timestamp,
  collection,
  doc,
  getDoc,
  getDocs,
  orderBy,
  query,
  where,
} from "firebase/firestore";
import { db } from "@/lib/firebase";

export interface SessionResponse {
  userId: string;
  startTime: Timestamp;
  endTime: Timestamp;
  durationSeconds: number;
  screenHeight: number;
  screenWidth: number;
}

export interface Session {
  id: string;
  userId: string;
  durationSeconds: number;
  startTime: Timestamp;
}

export async function getSession(sessionId: string): Promise<Session> {
  console.log("db is", db);
  console.log("sessionId is", sessionId);

  const response = await getDoc(doc(db, "sessions", sessionId));
  if (!response.exists()) {
    throw new Error("Session not found");
  }
  const data = response.data() as SessionResponse;
  return {
    id: response.id,
    userId: data.userId,
    durationSeconds: data.durationSeconds,
    startTime: data.startTime,
  };
}

export async function getUserSessions(userId: string): Promise<Session[]> {
  const q = query(
    collection(db, "sessions"),
    where("userId", "==", userId),
    orderBy("startTime", "desc")
  );

  const snap = await getDocs(q);

  return snap.docs.map((d) => {
    const data = d.data() as SessionResponse;
    return {
      id: d.id,
      userId: data.userId,
      durationSeconds: data.durationSeconds,
      startTime: data.startTime,
    };
  });
}
