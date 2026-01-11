import { Timestamp, doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export interface SessionResponse {
  user_id: string;
  start_time: Timestamp;
  end_time: Timestamp;
  duration_seconds: number;
  screen_height: number;
  screen_width: number;
}

export interface Session {
  id: string;
  userId: string;
  durationsSeconds?: number;
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
    userId: data.user_id,
    durationsSeconds: data.duration_seconds,
  };
}
