'use client';

import { login } from '../actions/auth';
import { useSearchParams } from 'next/navigation';

export default function LoginPage() {
    const searchParams = useSearchParams();
    const error = searchParams.get('error');

    return (
        <div style={{ padding: '2rem', maxWidth: 400, margin: '2rem auto', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h1>Connexion</h1>
            {error && <p style={{ color: 'red' }}>Identifiants incorrects</p>}
            <form action={login} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input 
                    name="email" 
                    type="email" 
                    placeholder="Email (ex: admin@taskflow.com)" 
                    required 
                    style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <input 
                    name="password" 
                    type="password" 
                    placeholder="Mot de passe" 
                    required 
                    style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <button type="submit" style={{
                    padding: '10px',
                    background: '#1B8C3E',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}>
                    Se connecter
                </button>
            </form>
        </div>
    );
}