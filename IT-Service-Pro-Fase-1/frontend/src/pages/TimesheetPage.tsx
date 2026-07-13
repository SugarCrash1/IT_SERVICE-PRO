import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {Clock3, Plus, Trash2} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import {useAuth} from '../auth/AuthContext';
import type {Employee, Project, TimeEntry, TimesheetSummary} from '../types';

const emptyForm = {empleado_id: '', proyecto_id: '', fecha: new Date().toISOString().slice(0, 10), minutos: '60', descripcion: '', facturable: true};

export function TimesheetPage() {
  const {user} = useAuth();
  const qc = useQueryClient();
  const esTecnico = user?.rol === 'TECNICO';
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const {data: registros = [], isLoading} = useQuery({queryKey: ['timesheet'], queryFn: async () => (await http.get('/timesheet')).data as TimeEntry[]});
  const {data: resumen} = useQuery({queryKey: ['timesheet-summary'], queryFn: async () => (await http.get('/timesheet/summary')).data as TimesheetSummary});
  const {data: tecnicos = []} = useQuery({queryKey: ['employees-all'], queryFn: async () => (await http.get('/employees', {params: {tamano_pagina: 100, estado: 'ACTIVO'}})).data.items as Employee[], enabled: !esTecnico});
  const {data: proyectos = []} = useQuery({queryKey: ['projects'], queryFn: async () => (await http.get('/projects')).data as Project[]});

  const invalidate = () => {qc.invalidateQueries({queryKey: ['timesheet']}); qc.invalidateQueries({queryKey: ['timesheet-summary']})};
  const crear = useMutation({
    mutationFn: () => http.post('/timesheet', {...form, empleado_id: form.empleado_id || undefined, proyecto_id: form.proyecto_id || undefined, minutos: Number(form.minutos)}),
    onSuccess: () => {toast.success('Horas registradas'); setOpen(false); setForm(emptyForm); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const eliminar = useMutation({
    mutationFn: (id: string) => http.delete(`/timesheet/${id}`),
    onSuccess: () => {toast.success('Registro eliminado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><Clock3 className="text-blue-600" />Registro de horas</h1>
          <p className="text-slate-500">Horas facturables y no facturables por técnico, ticket o proyecto.</p>
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}><Plus size={17} />Registrar horas</button>
      </div>

      {resumen && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="card"><p className="text-xs text-slate-500">Total registrado</p><p className="mt-1 text-2xl font-black">{resumen.total_horas}h</p></div>
          <div className="card"><p className="text-xs text-slate-500">Facturables</p><p className="mt-1 text-2xl font-black text-emerald-600">{resumen.horas_facturables}h</p></div>
          <div className="card"><p className="text-xs text-slate-500">No facturables</p><p className="mt-1 text-2xl font-black text-slate-500">{resumen.horas_no_facturables}h</p></div>
        </div>
      )}

      {isLoading ? <div className="card">Cargando registros...</div> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Fecha</th><th>Técnico</th><th>Descripción</th><th>Ticket/Proyecto</th><th>Horas</th><th>Facturable</th><th></th></tr></thead>
            <tbody>
              {registros.map(r => (
                <tr key={r.id}>
                  <td>{r.fecha}</td>
                  <td>{r.empleado_nombre}</td>
                  <td className="max-w-xs truncate">{r.descripcion}</td>
                  <td>{r.ticket_codigo || r.proyecto_nombre || '—'}</td>
                  <td>{(r.minutos / 60).toFixed(1)}h</td>
                  <td>{r.facturable ? <span className="badge bg-emerald-100 text-emerald-700">Sí</span> : <span className="badge bg-slate-200 text-slate-600">No</span>}</td>
                  <td><button className="btn-secondary !px-2.5 !py-1 text-xs text-rose-600" onClick={() => eliminar.mutate(r.id)}><Trash2 size={13} /></button></td>
                </tr>
              ))}
              {registros.length === 0 && <tr><td colSpan={7} className="py-8 text-center text-slate-400">No hay horas registradas</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={open} title="Registrar horas" onClose={() => setOpen(false)}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
          {!esTecnico && (
            <label className="sm:col-span-2"><span className="label">Técnico</span>
              <select className="field" required value={form.empleado_id} onChange={e => setForm({...form, empleado_id: e.target.value})}>
                <option value="">Selecciona un técnico</option>
                {tecnicos.map(t => <option key={t.id} value={t.id}>{t.nombre_completo}</option>)}
              </select>
            </label>
          )}
          <label><span className="label">Fecha</span><input type="date" className="field" required value={form.fecha} onChange={e => setForm({...form, fecha: e.target.value})} /></label>
          <label><span className="label">Minutos</span><input type="number" min={1} max={1440} className="field" required value={form.minutos} onChange={e => setForm({...form, minutos: e.target.value})} /></label>
          <label className="sm:col-span-2"><span className="label">Proyecto (opcional)</span>
            <select className="field" value={form.proyecto_id} onChange={e => setForm({...form, proyecto_id: e.target.value})}>
              <option value="">Sin proyecto asociado</option>
              {proyectos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
          </label>
          <label className="sm:col-span-2"><span className="label">Descripción</span><textarea className="field" required rows={3} value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} /></label>
          <label className="flex items-center gap-2 text-sm font-semibold sm:col-span-2"><input type="checkbox" checked={form.facturable} onChange={e => setForm({...form, facturable: e.target.checked})} />Horas facturables al cliente</label>
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending}>Guardar</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
