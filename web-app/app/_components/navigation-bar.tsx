"use client";

import { NAV_BAR } from "@/lib/constants";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu'
import React from 'react'
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { auth } from "@/lib/firebase";
import { signOut } from "firebase/auth";
import router from "next/router";
import { useAuthUser } from "@/lib/hooks/use-auth-user";

const pages: Array<{
  name: string;
  url: string;
}> = [
  { name: "Home", url: "/" },
  { name: "My Sessions", url: "/sessions" },
];

export default function NavigationBar(): React.JSX.Element {
  const { user, authReady } = useAuthUser();
  const router = useRouter();

  async function handleLogout() {
    await signOut(auth);
    router.push("/login");
  }

  return (
    <div className="flex w-full items-center justify-between">
    <div className="flex items-center gap-8">
      <span className="font-medium">{NAV_BAR.TITLE}</span>
      <NavMenu/>
    </div>
    {!authReady ? null : user ? (
        <Button onClick={handleLogout} className="cursor-pointer">
          Logout
        </Button>
      ) : (
        <Link href="/login">
          <Button className="cursor-pointer">Login</Button>
        </Link>
      )}
    </div>
  )
}

export function NavMenu() {
  const pathname = usePathname();

  return (
    <NavigationMenu>
      <NavigationMenuList>
        {pages.map(({ name, url }) => (
          <NavigationMenuItem key={url}>
            <NavigationMenuLink
              className={navigationMenuTriggerStyle()}
              active={pathname === url}
              asChild
            >
              <Link href={url}>{name}</Link>
            </NavigationMenuLink>
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  );
}
