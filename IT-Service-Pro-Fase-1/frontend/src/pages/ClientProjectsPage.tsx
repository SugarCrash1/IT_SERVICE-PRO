import {useQuery} from '@tanstack/react-query';
import {FolderKanban} from 'lucide-react';
import {http} from '../api/http';
import type {Project} from '../types';

const ESTADO_LABEL: Record<string, string> = {
  PLANIFICACION: 'En planificación', EN_CURSO: 'En curso', PAUSADO: 'Pausado', FINALIZADO: 'Finalizado', CANCELADO: 'Cancelado',
};
const ESTADO_COLOR: Record<string, string> = {
  PLANIFICACION: 'bg-slate-200 text-slate-600 dark:bg-slate-800',
  EN_CURSO: 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300',
  PAUSADO: 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300',
  FINALIZADO: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  CANCELADO: 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300',
};

export function ClientProjectsPage() {
  const {data: proyectos = [], isLoading} = useQuery({
    queryKey: ['client-projects'],
    queryFn: async () => (await http.get('/client-portal/projects')).data.data as Project[],
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title flex items-center gap-2"><FolderKanban className="text-blue-600" />Mis proyectos</h1>
        <p className="text-slate-500">Avance, tareas e hitos de los proyectos contratados con nosotros.</p>
      </div>

      {isLoading ? (
        <div className="card">Cargando proyectos...</div>
      ) : proyectos.length === 0 ? (
        <div className="card text-center text-slate-500">Tu empresa aún no tiene proyectos activos.</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {proyectos.map(p => (
            <article key={p.id} className="card">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-black text-blue-600">{p.codigo}</span>
                <span className={`badge ${ESTADO_COLOR[p.estado]}`}>{ESTADO_LABEL[p.estado]}</span>
              </div>
              <h2 className="mt-2 text-lg font-black">{p.nombre}</h2>
              {p.descripcion && <p className="mt-1 text-sm text-slate-500">{p.descripcion}</p>}
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div className="h-full bg-blue-600" style={{width: `${p.avance_porcentaje}%`}} />
              </div>
              <p className="mt-1.5 text-xs text-slate-400">{p.avance_porcentaje}% completado · {p.tareas_completadas}/{p.total_tareas} tareas</p>
              {p.responsable_nombre && <p className="mt-2 text-xs text-slate-500">Responsable: {p.responsable_nombre}</p>}
              {p.fecha_fin_estimada && <p className="text-xs text-slate-400">Entrega estimada: {p.fecha_fin_estimada}</p>}
              {p.tareas.length > 0 && (
                <details className="mt-3 text-sm">
                  <summary className="cursor-pointer font-semibold text-slate-500">Ver tareas ({p.tareas.length})</summary>
                  <ul className="mt-2 space-y-1">
                    {p.tareas.map(t => (
                      <li key={t.id} className={t.estado === 'COMPLETADA' ? 'text-slate-400 line-through' : ''}>• {t.titulo}</li>
                    ))}
                  </ul>
                </details>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
