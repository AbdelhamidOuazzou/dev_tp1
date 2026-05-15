// app/projects/[id]/page.tsx
import { notFound } from 'next/navigation';

interface Props {
    params: Promise<{ id: string }>;
}

export default async function ProjectPage({ params }: Props) {
    const { id } = await params;

    const res = await fetch(`http://localhost:4000/projects/${id}`, { cache: 'no-store' });
    
    if (!res.ok) {
        notFound();
    }

    const project = await res.json();

    return (
        <div style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ 
                    width: '24px', 
                    height: '24px', 
                    borderRadius: '50%', 
                    backgroundColor: project.color 
                }} />
                <h1 style={{ margin: 0 }}>{project.name}</h1>
            </div>
            <p>ID du projet : {id}</p>
            <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
                <h3>Tableau de bord du projet</h3>
                <p>Les colonnes et tâches seront affichées ici.</p>
            </div>
        </div>
    );
}
