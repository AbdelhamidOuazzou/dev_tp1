import AddProjectForm from './AddProjectForm';
import Link from 'next/link';

export default async function DashboardPage() {
    const res = await fetch('http://localhost:4000/projects', { cache: 'no-store' });
    const projects = await res.json();
    return (
        <div style={{ padding: '2rem' }}>
            <h1>Dashboard</h1>
            <AddProjectForm />
            <ul style={{ listStyle: 'none', padding: 0 }}>
                {projects.map((p: any) => (
                    <li key={p.id} style={{ marginBottom: '0.5rem' }}>
                        <Link href={`/projects/${p.id}`} style={{ 
                            textDecoration: 'none', 
                            color: 'inherit',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            <span style={{ 
                                width: '12px', 
                                height: '12px', 
                                borderRadius: '50%', 
                                backgroundColor: p.color 
                            }} />
                            {p.name}
                        </Link>
                    </li>
                ))}
            </ul>
        </div>
    );
}