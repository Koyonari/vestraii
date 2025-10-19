'use client'

import { Authenticated, Unauthenticated } from 'convex/react'
import { SignInButton, UserButton } from '@clerk/nextjs'
import { AppSidebar } from '@/components/AppSidebar'
import { useQuery } from 'convex/react'
import { api } from '../convex/_generated/api'

export default function Home() {
        return (
                <>
                        <Authenticated>
                                <AppSidebar />
                                <UserButton />
                                <Content />
                        </Authenticated>
                        <Unauthenticated>
                                <AppSidebar />
                                <SignInButton />
                        </Unauthenticated>
                </>
        )
}

function Content() {
        const messages = useQuery(api.messages.getForCurrentUser)
        return <div>Authenticated content: {messages?.length}</div>
}
