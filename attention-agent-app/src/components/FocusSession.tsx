import { useEffect, useRef, useState } from 'react';
import { getAuth } from 'firebase/auth';
import { getFirestore, collection, addDoc, serverTimestamp, query, where, orderBy, onSnapshot } from 'firebase/firestore';

export default function FocusSession() {
  const [running, setRunning] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const startRef = useRef<number | null>(null);

  const [sessions, setSessions] = useState<any[]>([]);
  const auth = getAuth();
  const db = getFirestore();

  useEffect(() => {
    const user = auth.currentUser;
    if (!user) return;

    const q = query(
      collection(db, 'sessions'),
      where('uid', '==', user.uid),
      orderBy('startedAt', 'desc')
    );

    return onSnapshot(q, (snap) => {
      setSessions(snap.docs.map(d => ({ id: d.id, ...d.data() })));
    });
  }, [auth.currentUser]);

  useEffect(() => {
    let id: number | undefined;
    if (running) {
      id = window.setInterval(() => setSeconds(s => s + 1), 1000);
    }
    return () => clearInterval(id);
  }, [running]);

  const start = () => {
    setSeconds(0);
    startRef.current = Date.now();
    setRunning(true);
  };

  const stopAndSave = async () => {
    setRunning(false);
    const user = auth.currentUser;
    if (!user || !startRef.current) return;

    const durationSec = Math.floor((Date.now() - startRef.current) / 1000);
    const distractionScore = Math.max(0, 100 - Math.floor(durationSec / 3)); // demo metric

    await addDoc(collection(db, 'sessions'), {
      uid: user.uid,
      startedAt: serverTimestamp(),
      durationSec,
      distractionScore,
    });
  };

  return (
    <div style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
      <h2>Focus Session</h2>
      <div style={{ fontSize: 28, fontFamily: 'monospace' }}>
        {String(Math.floor(seconds / 60)).padStart(2,'0')}:
        {String(seconds % 60).padStart(2,'0')}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={start} disabled={running}>Start</button>
        <button onClick={stopAndSave} disabled={!running}>Stop & Save</button>
      </div>

      <h3>Your Recent Sessions</h3>
      <div>Total: {sessions.length}</div>
      <ul>
        {sessions.map(s => (
          <li key={s.id}>
            duration: {s.durationSec ?? '…'}s · score: {s.distractionScore ?? '…'}
          </li>
        ))}
      </ul>
    </div>
  );
}
