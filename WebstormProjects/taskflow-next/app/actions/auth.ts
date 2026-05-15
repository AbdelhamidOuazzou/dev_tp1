'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export async function login(formData: FormData) {
    const email = formData.get('email');
    const password = formData.get('password');

    const res = await fetch('http://localhost:4000/users');
    const users = await res.json();

    const user = users.find((u: any) => u.email === email && u.password === password);

    if (user) {
        const cookieStore = await cookies();
        cookieStore.set('auth_token', 'user_logged_in', {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60 * 24 * 7, // 1 week
            path: '/',
        });
        redirect('/dashboard');
    } else {
        redirect('/login?error=1');
    }
}

export async function logout() {
    const cookieStore = await cookies();
    cookieStore.delete('auth_token');
    redirect('/login');
}
