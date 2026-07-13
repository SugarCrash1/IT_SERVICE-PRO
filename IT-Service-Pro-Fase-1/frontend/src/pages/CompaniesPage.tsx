import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {Building2, Globe2, Pencil, Plus, Power, Search, ShieldCheck} from 'lucide-react';
import toast from 'react-hot-toast';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';

const emptyForm = {razon_social: '', nombre_comercial: '', ruc: '', sector: 'Tecnología', correo: '', telefono: '', ciudad: 'Lima', nivel_sla: 'STANDARD'};

export function CompaniesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState(emptyForm);

  const {data = [], isLoading} = useQuery({queryKey: ['itsp-companies', search], queryFn: async () => (await http.get('/itsp/companies', {params: {search: search || undefined}})).data});

  const invalidate = () => qc.invalidateQueries({queryKey: ['itsp-companies']});
  const crear = useMutation({
    mutationFn: () => http.post('/itsp/companies', form),
    onSuccess: () => {toast.success('Empresa creada'); setOpen(false); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const actualizar = useMutation({
    mutationFn: () => http.put(`/itsp/companies/${editing.id}`, {
      razon_social: form.razon_social, nombre_comercial: form.nombre_comercial, sector: form.sector,
      correo: form.correo, telefono: form.telefono, ciudad: form.ciudad, nivel_sla: form.nivel_sla,
    }),
    onSuccess: () => {toast.success('Empresa actualizada'); setOpen(false); setEditing(null); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const toggleEstado = useMutation({
    mutationFn: ({id, estado}: {id: string; estado: string}) => http.patch(`/itsp/companies/${id}/status`, {estado}),
    onSuccess: () => {toast.success('Estado actualizado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const openCreate = () => {setEditing(null); setForm(emptyForm); setOpen(true)};
  const openEdit = (e: any) => {
    setEditing(e);
    setForm({razon_social: e.razon_social, nombre_comercial: e.nombre_comercial || '', ruc: e.ruc, sector: e.sector || '', correo: e.correo || '', telefono: e.telefono || '', ciudad: e.ciudad || '', nivel_sla: e.nivel_sla});
    setOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title">Empresas cliente</h1>
          <p className="text-slate-500">CRM corporativo y nivel de servicio contratado.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}><Plus size={17} />Nueva empresa</button>
      </div>

      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-slate-400" size={18} />
          <input className="field pl-10" placeholder="Buscar por razón social o nombre comercial" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      {isLoading ? <div className="card">Cargando empresas...</div> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.map((e: any) => (
            <article className="card" key={e.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-blue-100 text-blue-700 dark:bg-blue-950/50"><Building2 /></div>
                <span className={`badge ${e.estado === 'ACTIVO' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>{e.estado}</span>
              </div>
              <h2 className="mt-4 text-lg font-black">{e.nombre_comercial || e.razon_social}</h2>
              <p className="text-sm text-slate-500">{e.razon_social}</p>
              <div className="mt-5 space-y-2 text-sm">
                <p className="flex items-center gap-2"><ShieldCheck size={15} />SLA {e.nivel_sla}</p>
                <p className="flex items-center gap-2"><Globe2 size={15} />{e.ciudad || e.pais}</p>
                <p>RUC: {e.ruc}</p>
              </div>
              <div className="mt-4 flex gap-2">
                <button className="btn-secondary !px-3 !py-1.5 text-xs" onClick={() => openEdit(e)}><Pencil size={13} className="mr-1 inline" />Editar</button>
                <button className="btn-secondary !px-3 !py-1.5 text-xs" onClick={() => toggleEstado.mutate({id: e.id, estado: e.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'})}>
                  <Power size={13} className="mr-1 inline" />{e.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                </button>
              </div>
            </article>
          ))}
          {data.length === 0 && <div className="card text-center text-slate-400 md:col-span-2 xl:col-span-3">No hay empresas con este filtro</div>}
        </div>
      )}

      <Modal open={open} title={editing ? 'Editar empresa' : 'Nueva empresa'} onClose={() => {setOpen(false); setEditing(null)}}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); editing ? actualizar.mutate() : crear.mutate()}}>
          {Object.entries(form).map(([k, v]) => {
            if (k === 'ruc' && editing) return null;
            return (
              <label key={k} className={k === 'razon_social' ? 'sm:col-span-2' : ''}>
                <span className="label">{k.replaceAll('_', ' ')}</span>
                {k === 'nivel_sla' ? (
                  <select className="field" value={v} onChange={e => setForm({...form, [k]: e.target.value})}>
                    <option>STANDARD</option><option>GOLD</option><option>PLATINUM</option>
                  </select>
                ) : (
                  <input className="field" value={v} required={['razon_social', 'ruc'].includes(k)} onChange={e => setForm({...form, [k]: e.target.value})} />
                )}
              </label>
            );
          })}
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => {setOpen(false); setEditing(null)}}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending || actualizar.isPending}>{editing ? 'Guardar cambios' : 'Guardar'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
