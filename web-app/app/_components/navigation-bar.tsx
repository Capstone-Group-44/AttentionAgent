'use client'

import { NAV_BAR } from '@/lib/constants'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu'
import React from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
<<<<<<< HEAD
=======
import { Button } from '@/components/ui/button'
>>>>>>> b4bd96808304b5173cb064c081996a1eaf0a5ebe

const pages: Array<{
    name: string
    url: string
}> = [
<<<<<<< HEAD
    { name: 'Home', url: '/home'},
    { name: 'My Sessions', url: '/sessions'},
    { name: 'Community', url: '/community'},
=======
    { name: 'Home', url: '/'},
    { name: 'My Sessions', url: '/sessions'},
>>>>>>> b4bd96808304b5173cb064c081996a1eaf0a5ebe
]

export default function NavigationBar(): React.JSX.Element {
  return (
<<<<<<< HEAD
    <div className="flex items-center justify-between">
      <span className="font-medium">{NAV_BAR.TITLE}</span>
      <NavMenu/>
    </div>
=======
    <div className="flex w-full items-center justify-between">
    <div className="flex items-center gap-8">
      <span className="font-medium">{NAV_BAR.TITLE}</span>
      <NavMenu/>
    </div>
    <Link href="/login">
        <Button className="cursor-pointer">
          Login
        </Button>
      </Link>
    </div>
>>>>>>> b4bd96808304b5173cb064c081996a1eaf0a5ebe
  )
}

export function NavMenu() {
    const pathname = usePathname()

    return (
        <NavigationMenu>
            <NavigationMenuList >
                {pages.map(({ name, url }) => (
                    <NavigationMenuItem
                        key = {url}
                    >
                        <NavigationMenuLink
                            className={navigationMenuTriggerStyle()}
                            active={pathname === url}
                            asChild
                        >
                            <Link 
                                href={url}
                            >
                                {name}
                            </Link>
                        </NavigationMenuLink>    
                    </NavigationMenuItem>

                ))}
            </NavigationMenuList>
        </NavigationMenu>
    )
}