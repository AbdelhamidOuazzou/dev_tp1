import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import type {RootState} from '../../store';
import { loginStart, loginSuccess, loginFailure } from './authSlice';
import { setAuthToken } from '../../api/axios';
import api from '../../api/axios';
import styles from './Login.module.css';


export default function Login() {
    const navigate = useNavigate();
    const location = useLocation();
    const dispatch = useDispatch();
    const { user, loading, error } = useSelector((state: RootState) => state.auth);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const from = (location.state as { from?: string })?.from || '/dashboard';
    useEffect(() => {
        if (user) navigate(from, { replace: true })
    }, [user, navigate, from]);
    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        dispatch(loginStart());
        try {
            const { data: users } = await api.get(`/users?email=${email}`);
            if (users.length === 0 || users[0].password !== password) {
                dispatch(loginFailure('Email ou mot de passe incorrect'));
                return;
            }
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { password: _, ...userData } = users[0];
            const fakeToken = btoa(JSON.stringify({
                userId: userData.id,
                email: userData.email,
                role: 'admin',
                exp: Date.now() + 3600000 // expire dans 1h
            }));
            dispatch(loginSuccess({ user: userData, token: fakeToken }));
            setAuthToken(fakeToken);
        } catch {
            dispatch(loginFailure('Erreur serveur'));
        }
    }
    return (
        <div className={styles.container}>
            <form className={styles.form} onSubmit={handleSubmit}>
                <h1 className={styles.title}>TaskFlow</h1>
                <p className={styles.subtitle}>Connectez-vous pour continuer</p>
                {error && <div className={styles.error}>{error}</div>}
                <input type="email" placeholder="Email"
                       value={email} onChange={e => setEmail(e.target.value)}
                       className={styles.input} required />
                <input type="password" placeholder="Mot de passe"
                       value={password} onChange={e => setPassword(e.target.value)}
                       className={styles.input} required />
                <button type="submit" className={styles.button} disabled={loading}>
                    {loading ? 'Connexion...' : 'Se connecter'}
                </button>
            </form>
        </div>
    );
}