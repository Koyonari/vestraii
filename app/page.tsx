"use client";
import { Authenticated, Unauthenticated } from "convex/react";
import {  useClerk } from "@clerk/nextjs";
import Dashboard from "@/components/dashboard/dashboard";
import { useEffect } from "react";

export default function Home() {
  return (
    <>
      <Authenticated>
        <Dashboard />
      </Authenticated>
      <Unauthenticated>
        <UnauthenticatedContent />
      </Unauthenticated>
    </>
  );
}

function UnauthenticatedContent() {
  const { openSignIn } = useClerk();

  useEffect(() => {
    openSignIn();
  }, [openSignIn]);

  return <Dashboard />;
}

{/*
"use client";
import { Authenticated, Unauthenticated } from "convex/react";
import { SignInButton, UserButton } from "@clerk/nextjs";
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

export default function Home() {
  return (
    <>
      <Authenticated>
        <SignInButton />
        <UserButton />
        <AuthenticatedContent />
      </Authenticated>
      <Unauthenticated>
        <SignInButton />
        <UserButton />
        <UnauthenticatedContent />
      </Unauthenticated>
    </>
  );
}

function AuthenticatedContent() {
  const messages = useQuery(api.messages.getForCurrentUser);
  return <div>Authenticated content: {messages?.length}</div>;
}

function UnauthenticatedContent() {
  // Same UI, just without the query
  return <div>Unauthenticated content: 0</div>;
}
*/}
