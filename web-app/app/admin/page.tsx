"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { useRouter } from "next/navigation";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function AdminPage() {
  const { user, authReady } = useAuthUser();
  const router = useRouter();

  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 🔐 protect route
  useEffect(() => {
    if (authReady && (!user || user.role !== "admin")) {
      router.push("/");
    }
  }, [user, authReady]);

  // 📊 fetch users
  useEffect(() => {
    async function fetchUsers() {
      const snapshot = await getDocs(collection(db, "users"));
      const data = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      setUsers(data);
      setLoading(false);
    }

    if (user?.role === "admin") {
      fetchUsers();
    }
  }, [user]);

  if (!authReady || !user) return null;
  if (user.role !== "admin") return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Admin Dashboard</h1>

      {loading ? (
        <p>Loading users...</p>
      ) : (
        <div className="border rounded-lg p-4">
          <h2 className="font-medium mb-4">All Users</h2>

          <table className="w-full text-sm">
            <thead className="text-left border-b">
              <tr>
                <th className="py-2">Email</th>
                <th>Role</th>
                <th>Created</th>
              </tr>
            </thead>

            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b">
                  <td className="py-2">{u.email || "—"}</td>
                  <td>{u.role || "user"}</td>
                  <td>
                    {u.createdAt?.toDate?.().toLocaleDateString() || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}