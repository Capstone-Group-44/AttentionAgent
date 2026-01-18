// import Link from 'next/link'

// type SessionRowProps = {
//   sessionId: string
// }

// import type { Timestamp } from "firebase/firestore";


// export function SessionRow({ sessionId }: SessionRowProps) {
//   return (
//     <Link
//       href={`/sessions/${sessionId}`}
//       className="block hover:bg-muted/40 transition-colors cursor-pointer"
//     >
//     <div className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-6 px-6 py-5">
//       {/* Left side: date + started time */}
//       <div className="space-y-2">
//         <div className="h-4 w-40 rounded bg-muted" />
//         <div className="h-4 w-28 rounded bg-muted" />
//       </div>

//       {/* Duration */}
//       <div className="justify-self-end">
//         <div className="h-4 w-16 rounded bg-muted" />
//       </div>

//       {/* Sessions */}
//       <div className="justify-self-end">
//         <div className="h-4 w-8 rounded bg-muted" />
//       </div>

//       {/* Focus Score */}
//       <div className="justify-self-end flex items-center gap-2">
//         <div className="h-4 w-20 rounded bg-muted" />
//         <div className="h-2.5 w-2.5 rounded-full bg-muted" />
//       </div>
//     </div>
//     </Link>
//   )
// }
