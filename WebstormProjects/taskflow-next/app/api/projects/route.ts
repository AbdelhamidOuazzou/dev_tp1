import { NextResponse } from 'next/server';

export async function GET() {
    const res = await fetch('http://localhost:4000/projects');
    const projects = await res.json();
    return NextResponse.json(projects);
}
