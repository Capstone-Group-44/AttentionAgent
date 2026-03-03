import {
  collection,
  getDocs,
  orderBy,
  query,
  Timestamp,
} from "firebase/firestore";
import { db } from "@/lib/firebase";

export type FocusSample = {
  id: string;
  timestamp: Timestamp;
  focusScore: number; // 0..1
  attentionState?: number; // 0/1
};

type FocusSampleResponse = {
  timestamp: Timestamp;
  focusScore: number;
  attentionState?: number;
};

export async function getSessionFocusSamples(
  sessionId: string,
): Promise<FocusSample[]> {
  const q = query(
    collection(db, "sessions", sessionId, "focusSamples"),
    orderBy("timestamp", "asc"),
  );

  const snap = await getDocs(q);

  return snap.docs.map((d) => {
    const data = d.data() as FocusSampleResponse;
    return {
      id: d.id,
      timestamp: data.timestamp,
      focusScore: Number(data.focusScore ?? 0),
      attentionState: data.attentionState,
    };
  });
}
