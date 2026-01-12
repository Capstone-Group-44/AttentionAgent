"use client"

import { signOut } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { useRouter } from "next/navigation"
import { useAuthUser } from "@/lib/hooks/use-auth-user"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { SlidersHorizontal } from "lucide-react"

export function UserMenu() {
  const { user, authReady } = useAuthUser()
  const router = useRouter()

  if (!authReady) return null

  if (!user) {
    return (
      <Button onClick={() => router.push("/login")}>
        Login
      </Button>
    )
  }

  async function handleLogout() {
    await signOut(auth)
    router.push("/login")
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
        >
          <SlidersHorizontal className="size-6" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={handleLogout}>
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
