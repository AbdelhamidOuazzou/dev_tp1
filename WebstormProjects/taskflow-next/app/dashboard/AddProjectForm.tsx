'use client';
import { useFormStatus } from 'react-dom';
import { addProject } from '../actions/projects';
function SubmitButton() {
    const { pending } = useFormStatus();
    return (
        <button type="submit" disabled={pending} style={{
            padding: '8px 16px', background: '#1B8C3E', color: 'white',
            border: 'none', borderRadius: 4, cursor: 'pointer'
        }}>
            {pending ? 'Création...' : '+ Nouveau projet'}</button>
    );
}
export default function AddProjectForm() {
    return (
        <form action={addProject} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <input name="name" placeholder="Nom du projet" required
                   style={{ padding: 8, borderRadius: 4, border: '1px solid #ccc' }} />
            <input name="color" type="color" defaultValue="#3498db"
                   style={{ width: 40, height: 36, border: 'none' }} />
            <SubmitButton />
        </form>
    );
}