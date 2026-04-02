import { useState, useEffect } from 'react';
import { useAuth } from '../features/auth/AuthContext';
import api from '../api/axios';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import ProjectForm from '../components/ProjectForm';
import styles from './Dashboard.module.css';
import axios from 'axios';
import HeaderMUI from "../components/HeaderMUI";
import LoginBS from "./features/auth/LoginBS.tsx";

interface Project { id: string; name: string; color: string; }
interface Column { id: string; title: string; tasks: string[]; }

export default function Dashboard() {
    // 1. TOUS LES HOOKS SONT MAINTENANT À L'INTÉRIEUR DU COMPOSANT
    const { state: authState, dispatch } = useAuth();
    const [error, setError] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [projects, setProjects] = useState<Project[]>([]);
    const [columns, setColumns] = useState<Column[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);

    // GET — charger les données au montage
    useEffect(() => {
        async function fetchData() {
            try {
                const [projRes, colRes] = await Promise.all([
                    api.get('/projects'),
                    api.get('/columns'),
                ]);
                setProjects(projRes.data);
                setColumns(colRes.data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    // POST — ajouter un projet
    async function addProject(name: string, color: string) {
        setSaving(true);
        setError(null);
        try {
            const { data } = await api.post('/projects', { name, color });
            setProjects(prev => [...prev, data]);
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.message || `Erreur ${err.response?.status}`);
            } else {
                setError('Erreur inconnue');
            }
        } finally {
            setSaving(false);
        }
    }

    // PUT — renommer un projet
    async function renameProject(project: Project) {
        const nouveauNom = prompt('NewName', project.name);
        if (nouveauNom && nouveauNom !== project.name) {
            // CORRECTION ICI : virgule au lieu du signe +
            const { data } = await api.put(`/projects/${project.id}`, { ...project, name: nouveauNom });
            setProjects((pr) => pr.map((p) => (p.id === project.id ? data : p)));
        }
    }

    // DELETE — supprimer un projet
    async function deleteProject(id: string) {
        await api.delete(`/projects/${id}`);
        setProjects(prev => prev.filter((p) => p.id !== id));
    }

    if (loading) return <div className={styles.loading}>Chargement...</div>;

    return (
        <div className={styles.layout}>
            <HeaderMUI
                title="TaskFlow"
                onMenuClick={() => setSidebarOpen(p => !p)}
                userName={authState.user?.name}
                onLogout={() => dispatch({ type: 'LOGOUT' })}
            />
            <div className={styles.body}>
                <Sidebar projects={projects} isOpen={sidebarOpen} />
                <div className={styles.content}>
                    <div className={styles.toolbar}>
                        {!showForm ? (
                            <button className={styles.addBtn} onClick={() => setShowForm(true)}>
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

                    {/* Affichage d'erreur potentiel pour l'ajout de projet */}
                    {error && <div style={{ color: 'red', margin: '10px 0' }}>{error}</div>}
                    {saving && <div style={{ color: 'blue', margin: '10px 0' }}>Sauvegarde en cours...</div>}

                    <MainContent columns={columns} />
                </div>
            </div>
        </div>
    );
}