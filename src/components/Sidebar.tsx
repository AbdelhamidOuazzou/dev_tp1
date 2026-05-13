import styles from './Sidebar.module.css';
import { memo } from 'react';

interface Project { id: string; name: string; color: string; }
interface SidebarProps { projects: Project[]; isOpen: boolean; }

function Sidebar({ projects, isOpen }: SidebarProps) {
    return (
        <aside className={`${styles.sidebar} ${isOpen ? styles.open : styles.closed}`}>
            <h2 className={styles.title}>Mes Projets</h2>
            <ul className={styles.list}>
                {projects.map(p => (
                    <li key={p.id} className={styles.item}>
                        <span className={styles.dot} style={{ background: p.color }} />
                        {p.name}
                    </li>
                ))}
            </ul>
        </aside>
    );
}

export default memo(Sidebar);