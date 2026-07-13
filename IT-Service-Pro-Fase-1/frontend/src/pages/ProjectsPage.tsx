import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {CheckSquare, FolderKanban, Plus, Square} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {Company, Employee, Project} from '../types';

const ESTADOS = ['PLANIFICACION', 'EN_CURSO', 'PAUSADO', 'FINALIZADO', 'CANCELADO'];
const ESTADO_COLOR: Record<string, string> = {
  PLANIFICACION: 'bg-slate-200 text-slate-600 dark:bg-slate-800',
  EN_CURSO: 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300',
  PAUSADO: 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300',
  FINALIZADO: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  CANCELADO: 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300',
};
const emptyForm = {empresa_id: '', responsable_id: '', nombre: '', descripcion: '', fecha_inicio: '', fecha_fin_estimada: '', presupuesto: ''};

export function ProjectsPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [detailId, setDetailId] = useState<string | null>(null);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: tecnicos = []} = useQuery({queryKey: ['employees-all'], queryFn: async () => (await http.get('/employees', {params: {tamano_pagina: 100, estado: 'ACTIVO'}})).data.items as Employee[]});
  const {data: proyectos = [], isLoading} = useQuery({queryKey: ['projects'], queryFn: async () => (await http.get('/projects')).data as Project[]});

  const invalidate = () => qc.invalidateQueries({queryKey: ['projects']});
  const crear = useMutation({
    mutationFn: () => http.post('/projects', {...form, responsable_id: form.responsable_id || undefined, presupuesto: form.presupuesto ? Number(form.presupuesto) : undefined, fecha_inicio: form.fecha_inicio || undefined, fecha_fin_estimada: form.fecha_fin_estimada || undefined}),
    onSuccess: () => {toast.success('Proyecto creado'); setOpen(false); setForm(emptyForm); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const detalle = proyectos.find(p => p.id === detailId) || null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><FolderKanban className="text-blue-600" />Proyectos</h1>
          <p className="text-slate-500">Implementaciones y consultorías en curso por empresa cliente.</p>
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}><Plus size={17} />Nuevo proyecto</button>
      </div>

      {isLoading ? <div className="card">Cargando proyectos...</div> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {proyectos.map(p => (
            <button key={p.id} onClick={() => setDetailId(p.id)} className="card text-left hover:-translate-y-0.5 hover:shadow-lg transition">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-black text-blue-600">{p.codigo}</span>
                <span className={`badge ${ESTADO_COLOR[p.estado]}`}>{p.estado.replace('_', ' ')}</span>
              </div>
              <h2 className="mt-2 text-lg font-black">{p.nombre}</h2>
              <p className="text-sm text-slate-500">{p.empresa_nombre}</p>
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div className="h-full bg-blue-600" style={{width: `${p.avance_porcentaje}%`}} />
              </div>
              <p className="mt-1.5 text-xs text-slate-400">{p.avance_porcentaje}% · {p.tareas_completadas}/{p.total_tareas} tareas · {p.responsable_nombre || 'Sin responsable'}</p>
            </button>
          ))}
          {proyectos.length === 0 && <div className="card text-center text-slate-400 md:col-span-2 xl:col-span-3">Aún no hay proyectos registrados</div>}
        </div>
      )}

      <Modal open={open} title="Nuevo proyecto" onClose={() => setOpen(false)}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
          <label className="sm:col-span-2"><span className="label">Empresa</span>
            <select className="field" required value={form.empresa_id} onChange={e => setForm({...form, empresa_id: e.target.value})}>
              <option value="">Selecciona una empresa</option>
              {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
            </select>
          </label>
          <label className="sm:col-span-2"><span className="label">Nombre del proyecto</span>
            <input className="field" required value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
          </label>
          <label className="sm:col-span-2"><span className="label">Descripción</span>
            <textarea className="field" rows={3} value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} />
          </label>
          <label><span className="label">Responsable</span>
            <select className="field" value={form.responsable_id} onChange={e => setForm({...form, responsable_id: e.target.value})}>
              <option value="">Sin responsable</option>
              {tecnicos.map(t => <option key={t.id} value={t.id}>{t.nombre_completo}</option>)}
            </select>
          </label>
          <label><span className="label">Presupuesto (S/)</span><input type="number" min={0} className="field" value={form.presupuesto} onChange={e => setForm({...form, presupuesto: e.target.value})} /></label>
          <label><span className="label">Fecha de inicio</span><input type="date" className="field" value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} /></label>
          <label><span className="label">Fin estimado</span><input type="date" className="field" value={form.fecha_fin_estimada} onChange={e => setForm({...form, fecha_fin_estimada: e.target.value})} /></label>
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending}>Crear proyecto</button>
          </div>
        </form>
      </Modal>

      {detalle && <ProjectDetailModal project={detalle} tecnicos={tecnicos} onClose={() => setDetailId(null)} onChanged={invalidate} />}
    </div>
  );
}

function ProjectDetailModal({project, tecnicos, onClose, onChanged}: {project: Project; tecnicos: Employee[]; onClose: () => void; onChanged: () => void}) {
  const [nuevaTarea, setNuevaTarea] = useState('');
  const [avance, setAvance] = useState(project.avance_porcentaje);
  const [estado, setEstado] = useState(project.estado);

  const crearTarea = useMutation({
    mutationFn: () => http.post(`/projects/${project.id}/tasks`, {titulo: nuevaTarea}),
    onSuccess: () => {setNuevaTarea(''); onChanged()},
    onError: e => toast.error(errorMessage(e)),
  });
  const toggleTarea = useMutation({
    mutationFn: ({id, estado}: {id: string; estado: string}) => http.put(`/projects/${project.id}/tasks/${id}`, {estado}),
    onSuccess: onChanged,
    onError: e => toast.error(errorMessage(e)),
  });
  const guardarProyecto = useMutation({
    mutationFn: () => http.put(`/projects/${project.id}`, {avance_porcentaje: avance, estado}),
    onSuccess: () => {toast.success('Proyecto actualizado'); onChanged()},
    onError: e => toast.error(errorMessage(e)),
  });

  return (
    <Modal open title={`${project.codigo} · ${project.nombre}`} onClose={onClose}>
      <div className="space-y-5">
        <p className="text-sm text-slate-500">{project.empresa_nombre} · {project.descripcion || 'Sin descripción'}</p>

        <div className="grid gap-3 sm:grid-cols-2">
          <label><span className="label">Estado</span>
            <select className="field" value={estado} onChange={e => setEstado(e.target.value)}>
              {ESTADOS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
            </select>
          </label>
          <label><span className="label">Avance ({avance}%)</span>
            <input type="range" min={0} max={100} value={avance} onChange={e => setAvance(Number(e.target.value))} className="w-full" />
          </label>
        </div>
        <button className="btn-secondary" onClick={() => guardarProyecto.mutate()} disabled={guardarProyecto.isPending}>Guardar cambios</button>

        <div>
          <h3 className="text-sm font-black">Tareas ({project.tareas_completadas}/{project.total_tareas})</h3>
          <div className="mt-2 space-y-1.5">
            {project.tareas.map(t => (
              <div key={t.id} className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                <button onClick={() => toggleTarea.mutate({id: t.id, estado: t.estado === 'COMPLETADA' ? 'PENDIENTE' : 'COMPLETADA'})}>
                  {t.estado === 'COMPLETADA' ? <CheckSquare size={16} className="text-emerald-600" /> : <Square size={16} className="text-slate-400" />}
                </button>
                <span className={t.estado === 'COMPLETADA' ? 'flex-1 line-through text-slate-400' : 'flex-1'}>{t.titulo}</span>
                {t.responsable_nombre && <span className="text-xs text-slate-400">{t.responsable_nombre}</span>}
              </div>
            ))}
            {project.tareas.length === 0 && <p className="text-sm text-slate-400">Sin tareas todavía.</p>}
          </div>
          <form className="mt-3 flex gap-2" onSubmit={e => {e.preventDefault(); if (nuevaTarea.trim()) crearTarea.mutate()}}>
            <input className="field" placeholder="Nueva tarea..." value={nuevaTarea} onChange={e => setNuevaTarea(e.target.value)} />
            <button className="btn-primary !px-4" disabled={crearTarea.isPending}>Agregar</button>
          </form>
        </div>
      </div>
    </Modal>
  );
}
