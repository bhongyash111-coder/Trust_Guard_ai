'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to welcome page on mount
    router.push('/welcome');
  }, [router]);

  return null;
}
