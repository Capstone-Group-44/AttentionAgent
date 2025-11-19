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

const pages: Array<{
    name: string
    url: string
}> = [
    { name: 'Home', url: '/home'},
    { name: 'My Sessions', url: '/sessions'},
    { name: 'Community', url: '/community'},
]

export default function NavigationBar(): React.JSX.Element {
  return (
    <div className="flex items-center justify-between">
      <span className="font-medium">{NAV_BAR.TITLE}</span>
      <NavMenu/>
    </div>
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