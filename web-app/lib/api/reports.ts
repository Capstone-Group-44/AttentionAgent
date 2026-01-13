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
  avgFocusScore: number;
  createdAt: Timestamp;
  notes: string;
  sessionId: string;
  totalDistractionTime: number;
  totalFocusTime: number;
  userId: string;
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
    avgFocusScore: data.avgFocusScore,
    sessionId: data.sessionId,
    totalDistractionTime: data.totalDistractionTime,
    totalFocusTime: data.totalFocusTime,
  };
}

export async function getUserReports(userId: string): Promise<Report[]> {
  const q = query(
    collection(db, "reports"),
    where("userId", "==", userId),
    orderBy("createdAt", "desc")
  );

  const snap = await getDocs(q);

  return snap.docs.map((d) => {
    const data = d.data() as ReportResponse;
    return {
      avgFocusScore: data.avgFocusScore,
      sessionId: data.sessionId,
      totalDistractionTime: data.totalDistractionTime,
      totalFocusTime: data.totalFocusTime,
      createdAt: data.createdAt,
    };
  });
}
