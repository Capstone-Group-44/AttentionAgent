import { Timestamp, doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export interface SessionResponse {
  userID: string;
  startTime: Timestamp;
  endTime: Timestamp;
  durationSeconds: number;
  screenHeight: number;
  screenWidth: number;
}

export interface Session {
  id: string;
  userId: string;
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
    userId: data.userID,
  };
}
