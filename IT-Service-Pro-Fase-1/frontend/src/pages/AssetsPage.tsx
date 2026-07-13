import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {AlertTriangle, HardDrive, Plus, Search, Server} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {Asset, Company, Contact} from '../types';

const TIPOS = ['SERVIDOR', 'LAPTOP', 'DESKTOP', 'IMPRESORA', 'RED', 'LICENCIA', 'TELEFONIA', 'OTRO'];
const ESTADOS = ['ACTIVO', 'EN_MANTENIMIENTO', 'DADO_DE_BAJA'];
const ESTADO_COLOR: Record<string, string> = {
  ACTIVO: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  EN_MANTENIMIENTO: 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300',
  DADO_DE_BAJA: 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
};
const emptyForm = {empresa_id: '', responsable_id: '', tipo: 'OTRO', nombre: '', marca: '', modelo: '', numero_serie: '', ubicacion: '', ip_asignada: '', fecha_compra: '', fecha_garantia_fin: '', notas: ''};

export function AssetsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [empresaFiltro, setEmpresaFiltro] = useState('');
  const [tipoFiltro, setTipoFiltro] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Asset | null>(null);
  const [form, setForm] = useState(emptyForm);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: contactos = []} = useQuery({queryKey: ['itsp-contacts', form.empresa_id], queryFn: async () => form.empresa_id ? (await http.get('/itsp/contacts', {params: {empresa_id: form.empresa_id}})).data as Contact[] : [], enabled: !!form.empresa_id});
  const {data: activos = [], isLoading} = useQuery({
    queryKey: ['assets', empresaFiltro, tipoFiltro, search],
    queryFn: async () => (await http.get('/assets', {params: {empresa_id: empresaFiltro || undefined, tipo: tipoFiltro || undefined, busqueda: search || undefined}})).data as Asset[],
  });

  const invalidate = () => qc.invalidateQueries({queryKey: ['assets']});

  const crear = useMutation({
    mutationFn: () => http.post('/assets', {...form, responsable_id: form.responsable_id || undefined, fecha_compra: form.fecha_compra || undefined, fecha_garantia_fin: form.fecha_garantia_fin || undefined}),
    onSuccess: () => {toast.success('Activo registrado'); setOpen(false); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const actualizar = useMutation({
    mutationFn: () => http.put(`/assets/${editing!.id}`, {
      responsable_id: form.responsable_id || undefined, tipo: form.tipo, nombre: form.nombre, marca: form.marca || undefined,
      modelo: form.modelo || undefined, numero_serie: form.numero_serie || undefined, ubicacion: form.ubicacion || undefined,
      ip_asignada: form.ip_asignada || undefined, fecha_compra: form.fecha_compra || undefined,
      fecha_garantia_fin: form.fecha_garantia_fin || undefined, notas: form.notas || undefined,
    }),
    onSuccess: () => {toast.success('Activo actualizado'); setOpen(false); setEditing(null); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const cambiarEstado = useMutation({
    mutationFn: ({id, estado}: {id: string; estado: string}) => http.patch(`/assets/${id}/status`, {estado}),
    onSuccess: () => {toast.success('Estado actualizado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const eliminar = useMutation({
    mutationFn: (id: string) => http.delete(`/assets/${id}`),
    onSuccess: () => {toast.success('Activo eliminado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const openCreate = () => {setEditing(null); setForm({...emptyForm, empresa_id: empresaFiltro}); setOpen(true)};
  const openEdit = (a: Asset) => {
    setEditing(a);
    setForm({empresa_id: a.empresa_id, responsable_id: a.responsable_id || '', tipo: a.tipo, nombre: a.nombre, marca: a.marca || '', modelo: a.modelo || '', numero_serie: a.numero_serie || '', ubicacion: a.ubicacion || '', ip_asignada: a.ip_asignada || '', fecha_compra: a.fecha_compra?.slice(0, 10) || '', fecha_garantia_fin: a.fecha_garantia_fin?.slice(0, 10) || '', notas: a.notas || ''});
    setOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><Server className="text-blue-600" />CMDB — Activos</h1>
          <p className="text-slate-500">Servidores, equipos, licencias y su garantía por empresa cliente.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}><Plus size={17} />Nuevo activo</button>
      </div>

      <div className="card flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-3 text-slate-400" size={18} />
          <input className="field pl-10" placeholder="Buscar por nombre, código o serie" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="field w-auto" value={empresaFiltro} onChange={e => setEmpresaFiltro(e.target.value)}>
          <option value="">Todas las empresas</option>
          {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
        </select>
        <select className="field w-auto" value={tipoFiltro} onChange={e => setTipoFiltro(e.target.value)}>
          <option value="">Todo tipo</option>
          {TIPOS.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      {isLoading ? <div className="card">Cargando activos...</div> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Código</th><th>Activo</th><th>Empresa</th><th>Tipo</th><th>Responsable</th><th>Garantía</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {activos.map(a => (
                <tr key={a.id}>
                  <td className="font-black text-blue-600">{a.codigo}</td>
                  <td><p className="font-bold">{a.nombre}</p><p className="text-xs text-slate-400">{[a.marca, a.modelo].filter(Boolean).join(' · ') || '—'}</p></td>
                  <td>{a.empresa_nombre}</td>
                  <td className="flex items-center gap-1.5"><HardDrive size={14} className="text-slate-400" />{a.tipo}</td>
                  <td>{a.responsable_nombre || <span className="text-slate-400">—</span>}</td>
                  <td className={a.garantia_vencida ? 'font-bold text-rose-600' : ''}>
                    {a.fecha_garantia_fin ? a.fecha_garantia_fin : '—'}
                    {a.garantia_vencida && <span className="ml-1 inline-flex items-center gap-1 text-xs"><AlertTriangle size={12} />vencida</span>}
                  </td>
                  <td><span className={`badge ${ESTADO_COLOR[a.estado]}`}>{a.estado}</span></td>
                  <td>
                    <div className="flex flex-wrap gap-1.5">
                      <button className="btn-secondary !px-2.5 !py-1 text-xs" onClick={() => openEdit(a)}>Editar</button>
                      <select className="field !w-auto !py-1 text-xs" value={a.estado} onChange={e => cambiarEstado.mutate({id: a.id, estado: e.target.value})}>
                        {ESTADOS.map(s => <option key={s} value={s}>{s}</option>)}
                      </select>
                      <button className="btn-secondary !px-2.5 !py-1 text-xs text-rose-600" onClick={() => {if (confirm('¿Eliminar este activo?')) eliminar.mutate(a.id)}}>Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
              {activos.length === 0 && <tr><td colSpan={8} className="py-8 text-center text-slate-400">No hay activos con estos filtros</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={open} title={editing ? 'Editar activo' : 'Nuevo activo'} onClose={() => {setOpen(false); setEditing(null)}}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); editing ? actualizar.mutate() : crear.mutate()}}>
          <label className="sm:col-span-2"><span className="label">Empresa</span>
            <select className="field" required disabled={!!editing} value={form.empresa_id} onChange={e => setForm({...form, empresa_id: e.target.value, responsable_id: ''})}>
              <option value="">Selecciona una empresa</option>
              {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
            </select>
          </label>
          <label><span className="label">Tipo</span>
            <select className="field" value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})}>
              {TIPOS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label><span className="label">Responsable (opcional)</span>
            <select className="field" value={form.responsable_id} onChange={e => setForm({...form, responsable_id: e.target.value})} disabled={!form.empresa_id}>
              <option value="">Sin responsable</option>
              {contactos.map(c => <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>)}
            </select>
          </label>
          <label className="sm:col-span-2"><span className="label">Nombre del activo</span>
            <input className="field" required maxLength={150} value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
          </label>
          <label><span className="label">Marca</span><input className="field" value={form.marca} onChange={e => setForm({...form, marca: e.target.value})} /></label>
          <label><span className="label">Modelo</span><input className="field" value={form.modelo} onChange={e => setForm({...form, modelo: e.target.value})} /></label>
          <label><span className="label">Número de serie</span><input className="field" value={form.numero_serie} onChange={e => setForm({...form, numero_serie: e.target.value})} /></label>
          <label><span className="label">Ubicación</span><input className="field" value={form.ubicacion} onChange={e => setForm({...form, ubicacion: e.target.value})} /></label>
          <label><span className="label">IP asignada</span><input className="field" value={form.ip_asignada} onChange={e => setForm({...form, ip_asignada: e.target.value})} /></label>
          <label><span className="label">Fecha de compra</span><input type="date" className="field" value={form.fecha_compra} onChange={e => setForm({...form, fecha_compra: e.target.value})} /></label>
          <label><span className="label">Fin de garantía</span><input type="date" className="field" value={form.fecha_garantia_fin} onChange={e => setForm({...form, fecha_garantia_fin: e.target.value})} /></label>
          <label className="sm:col-span-2"><span className="label">Notas</span><textarea className="field" rows={3} value={form.notas} onChange={e => setForm({...form, notas: e.target.value})} /></label>
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => {setOpen(false); setEditing(null)}}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending || actualizar.isPending}>{editing ? 'Guardar cambios' : 'Registrar activo'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
