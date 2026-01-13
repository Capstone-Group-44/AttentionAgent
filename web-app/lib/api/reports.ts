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

export interface ReportResponse {
  avg_focus_score: number;
  created_at: Timestamp;
  notes: string;
  session_id: string;
  total_distraction_time: number;
  total_focus_time: number;
  user_id: string;
}

export interface Report {
  avgFocusScore: number;
  sessionId: string;
  totalDistractionTime: number;
  totalFocusTime: number;
}

export async function getReport(sessionId: string): Promise<Report> {
  console.log("sessionId is", sessionId);

  const response = await getDoc(doc(db, "reports", sessionId));
  if (!response.exists()) {
    throw new Error("Session not found");
  }
  const data = response.data() as ReportResponse;
  return {
    avgFocusScore: data.avg_focus_score,
    sessionId: data.session_id,
    totalDistractionTime: data.total_distraction_time,
    totalFocusTime: data.total_focus_time,
  };
}

export async function getUserReports(userId: string): Promise<Report[]> {
  const q = query(
    collection(db, "reports"),
    where("user_id", "==", userId),
    orderBy("created_at", "desc")
  );

  const snap = await getDocs(q);

  return snap.docs.map((d) => {
    const data = d.data() as ReportResponse;
    return {
      avgFocusScore: data.avg_focus_score,
      sessionId: data.session_id,
      totalDistractionTime: data.total_distraction_time,
      totalFocusTime: data.total_focus_time,
      createdAt: data.created_at,
    };
  });
}
