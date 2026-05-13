import { useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import type {RootState} from '../store';
import { logout } from '../features/auth/authSlice';
import { setAuthToken } from '../api/axios';
import useProjects from '../hooks/useProjects';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import ProjectForm from '../components/ProjectForm';
import styles from './Dashboard.module.css';

export default function Dashboard() {
    const user = useSelector((state: RootState) => state.auth.user);
    const dispatch = useDispatch();
    const { projects, columns, loading, error, addProject } = useProjects();
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [showForm, setShowForm] = useState(false);

    const handleLogout = useCallback(() => {
        dispatch(logout());
        setAuthToken(null);
    }, [dispatch]);

    if (loading) return <div className={styles.loading}>Chargement...</div>;
    return (
        <div className={styles.layout}>
            <Header
                title="TaskFlow"
                onMenuClick={() => setSidebarOpen(p => !p)}
                userName={user?.name}
                onLogout={handleLogout}
            />
            {error && <div className={styles.error}>{error}</div>}
            <div className={styles.body}>
                <Sidebar projects={projects} isOpen={sidebarOpen} />
                <div className={styles.content}>
                    <div className={styles.toolbar}>
                        {!showForm ? (
                            <button className={styles.addBtn}
                                    onClick={() => setShowForm(true)}>
                                + Nouveau projet
                            </button>
                        ) : (
                            <ProjectForm
                                submitLabel="Créer"
                                onSubmit={(name, color) => {
                                    addProject(name, color);
                                    setShowForm(false);
                                }}
                                onCancel={() => setShowForm(false)}
                            />
                        )}
                    </div>
                    <MainContent columns={columns} />
                </div>
            </div>
        </div>
    );
}