import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {Mail, Phone, Plus, Search, ShieldCheck, Star, UserRound} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {Company, Contact} from '../types';

const emptyForm = {empresa_id: '', nombres: '', apellidos: '', cargo: '', area: '', correo: '', telefono: '', puede_crear_tickets: true, es_contacto_principal: false};

export function ContactsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [empresaFiltro, setEmpresaFiltro] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Contact | null>(null);
  const [form, setForm] = useState(emptyForm);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: contactos = [], isLoading} = useQuery({
    queryKey: ['itsp-contacts', empresaFiltro],
    queryFn: async () => (await http.get('/itsp/contacts', {params: {empresa_id: empresaFiltro || undefined}})).data as Contact[],
  });

  const filtrados = contactos.filter(c => !search || `${c.nombres} ${c.apellidos} ${c.correo}`.toLowerCase().includes(search.toLowerCase()));
  const empresaNombre = (id: string) => empresas.find(e => e.id === id)?.nombre_comercial || empresas.find(e => e.id === id)?.razon_social || '—';

  const invalidate = () => {qc.invalidateQueries({queryKey: ['itsp-contacts']})};

  const crear = useMutation({
    mutationFn: () => http.post('/itsp/contacts', form),
    onSuccess: () => {toast.success('Contacto creado'); setOpen(false); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const actualizar = useMutation({
    mutationFn: () => http.put(`/itsp/contacts/${editing!.id}`, {
      nombres: form.nombres, apellidos: form.apellidos, cargo: form.cargo, area: form.area,
      correo: form.correo, telefono: form.telefono, puede_crear_tickets: form.puede_crear_tickets,
      es_contacto_principal: form.es_contacto_principal,
    }),
    onSuccess: () => {toast.success('Contacto actualizado'); setOpen(false); setEditing(null); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const toggleEstado = useMutation({
    mutationFn: ({id, estado}: {id: string; estado: string}) => http.patch(`/itsp/contacts/${id}/status`, {estado}),
    onSuccess: () => {toast.success('Estado actualizado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const eliminar = useMutation({
    mutationFn: (id: string) => http.delete(`/itsp/contacts/${id}`),
    onSuccess: () => {toast.success('Contacto eliminado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const openCreate = () => {setEditing(null); setForm({...emptyForm, empresa_id: empresaFiltro}); setOpen(true)};
  const openEdit = (c: Contact) => {
    setEditing(c);
    setForm({empresa_id: c.empresa_id, nombres: c.nombres, apellidos: c.apellidos, cargo: c.cargo || '', area: c.area || '', correo: c.correo, telefono: c.telefono || '', puede_crear_tickets: c.puede_crear_tickets, es_contacto_principal: c.es_contacto_principal});
    setOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title">Contactos empresariales</h1>
          <p className="text-slate-500">Responsables y usuarios autorizados a crear tickets por empresa.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}><Plus size={17} />Nuevo contacto</button>
      </div>

      <div className="card flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-3 text-slate-400" size={18} />
          <input className="field pl-10" placeholder="Buscar por nombre o correo" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="field w-auto" value={empresaFiltro} onChange={e => setEmpresaFiltro(e.target.value)}>
          <option value="">Todas las empresas</option>
          {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
        </select>
      </div>

      {isLoading ? <div className="card">Cargando contactos...</div> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtrados.map(c => (
            <article className="card" key={c.id}>
              <div className="flex items-start justify-between gap-2">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-blue-100 text-blue-700 dark:bg-blue-950/50"><UserRound /></div>
                <div className="flex items-center gap-1">
                  {c.es_contacto_principal && <span title="Contacto principal"><Star size={16} className="text-amber-500" /></span>}
                  <span className={`badge ${c.estado === 'ACTIVO' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>{c.estado}</span>
                </div>
              </div>
              <h2 className="mt-3 text-lg font-black">{c.nombres} {c.apellidos}</h2>
              <p className="text-sm text-slate-500">{c.cargo || 'Sin cargo'} · {empresaNombre(c.empresa_id)}</p>
              <div className="mt-3 space-y-1.5 text-sm">
                <p className="flex items-center gap-2"><Mail size={14} className="text-slate-400" />{c.correo}</p>
                {c.telefono && <p className="flex items-center gap-2"><Phone size={14} className="text-slate-400" />{c.telefono}</p>}
                {c.puede_crear_tickets && <p className="flex items-center gap-2 text-emerald-600"><ShieldCheck size={14} />Puede crear tickets</p>}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button className="btn-secondary !px-3 !py-1.5 text-xs" onClick={() => openEdit(c)}>Editar</button>
                <button className="btn-secondary !px-3 !py-1.5 text-xs" onClick={() => toggleEstado.mutate({id: c.id, estado: c.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'})}>
                  {c.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                </button>
                <button className="btn-secondary !px-3 !py-1.5 text-xs text-rose-600" onClick={() => {if (confirm('¿Eliminar este contacto?')) eliminar.mutate(c.id)}}>Eliminar</button>
              </div>
            </article>
          ))}
          {filtrados.length === 0 && <div className="card text-center text-slate-400 md:col-span-2 xl:col-span-3">No hay contactos con estos filtros</div>}
        </div>
      )}

      <Modal open={open} title={editing ? 'Editar contacto' : 'Nuevo contacto'} onClose={() => {setOpen(false); setEditing(null)}}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); editing ? actualizar.mutate() : crear.mutate()}}>
          {!editing && (
            <label className="sm:col-span-2"><span className="label">Empresa</span>
              <select className="field" required value={form.empresa_id} onChange={e => setForm({...form, empresa_id: e.target.value})}>
                <option value="">Selecciona una empresa</option>
                {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
              </select>
            </label>
          )}
          <label><span className="label">Nombres</span><input className="field" required value={form.nombres} onChange={e => setForm({...form, nombres: e.target.value})} /></label>
          <label><span className="label">Apellidos</span><input className="field" required value={form.apellidos} onChange={e => setForm({...form, apellidos: e.target.value})} /></label>
          <label><span className="label">Cargo</span><input className="field" value={form.cargo} onChange={e => setForm({...form, cargo: e.target.value})} /></label>
          <label><span className="label">Área</span><input className="field" value={form.area} onChange={e => setForm({...form, area: e.target.value})} /></label>
          <label><span className="label">Correo</span><input type="email" className="field" required value={form.correo} onChange={e => setForm({...form, correo: e.target.value})} /></label>
          <label><span className="label">Teléfono</span><input className="field" value={form.telefono} onChange={e => setForm({...form, telefono: e.target.value})} /></label>
          <label className="flex items-center gap-2 text-sm font-semibold"><input type="checkbox" checked={form.puede_crear_tickets} onChange={e => setForm({...form, puede_crear_tickets: e.target.checked})} />Puede crear tickets desde el portal</label>
          <label className="flex items-center gap-2 text-sm font-semibold"><input type="checkbox" checked={form.es_contacto_principal} onChange={e => setForm({...form, es_contacto_principal: e.target.checked})} />Es el contacto principal</label>
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => {setOpen(false); setEditing(null)}}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending || actualizar.isPending}>{editing ? 'Guardar cambios' : 'Crear contacto'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
