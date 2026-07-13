import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {AlertTriangle, BriefcaseBusiness, Plus} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {Company, Contract} from '../types';

const TIPOS = ['SOPORTE', 'BOLSA_HORAS', 'PROYECTO', 'LICENCIAMIENTO', 'OTRO'];
const ESTADOS = ['VIGENTE', 'VENCIDO', 'CANCELADO'];
const ESTADO_COLOR: Record<string, string> = {
  VIGENTE: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  VENCIDO: 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300',
  CANCELADO: 'bg-slate-200 text-slate-600 dark:bg-slate-800',
};
const emptyForm = {empresa_id: '', nombre: '', tipo: 'SOPORTE', fecha_inicio: '', fecha_fin: '', horas_incluidas_mes: '', valor_mensual: '', notas: ''};

export function ContractsPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Contract | null>(null);
  const [form, setForm] = useState(emptyForm);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: contratos = [], isLoading} = useQuery({queryKey: ['contracts'], queryFn: async () => (await http.get('/contracts')).data as Contract[]});

  const invalidate = () => qc.invalidateQueries({queryKey: ['contracts']});
  const crear = useMutation({
    mutationFn: () => http.post('/contracts', {...form, horas_incluidas_mes: form.horas_incluidas_mes ? Number(form.horas_incluidas_mes) : undefined, valor_mensual: form.valor_mensual ? Number(form.valor_mensual) : undefined, fecha_fin: form.fecha_fin || undefined}),
    onSuccess: () => {toast.success('Contrato creado'); setOpen(false); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const actualizar = useMutation({
    mutationFn: () => http.put(`/contracts/${editing!.id}`, {
      nombre: form.nombre, tipo: form.tipo, fecha_inicio: form.fecha_inicio, fecha_fin: form.fecha_fin || undefined,
      horas_incluidas_mes: form.horas_incluidas_mes ? Number(form.horas_incluidas_mes) : undefined,
      valor_mensual: form.valor_mensual ? Number(form.valor_mensual) : undefined, notas: form.notas || undefined,
    }),
    onSuccess: () => {toast.success('Contrato actualizado'); setOpen(false); setEditing(null); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const cambiarEstado = useMutation({
    mutationFn: ({id, estado}: {id: string; estado: string}) => http.put(`/contracts/${id}`, {estado}),
    onSuccess: () => {toast.success('Estado actualizado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const openCreate = () => {setEditing(null); setForm(emptyForm); setOpen(true)};
  const openEdit = (c: Contract) => {
    setEditing(c);
    setForm({empresa_id: c.empresa_id, nombre: c.nombre, tipo: c.tipo, fecha_inicio: c.fecha_inicio.slice(0, 10), fecha_fin: c.fecha_fin?.slice(0, 10) || '', horas_incluidas_mes: c.horas_incluidas_mes?.toString() || '', valor_mensual: c.valor_mensual?.toString() || '', notas: c.notas || ''});
    setOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><BriefcaseBusiness className="text-blue-600" />Contratos</h1>
          <p className="text-slate-500">SLA, bolsas de horas y vigencia de contratos por empresa.</p>
        </div>
        <button className="btn-primary" onClick={openCreate}><Plus size={17} />Nuevo contrato</button>
      </div>

      {isLoading ? <div className="card">Cargando contratos...</div> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Código</th><th>Contrato</th><th>Empresa</th><th>Tipo</th><th>Horas/mes</th><th>Vigencia</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {contratos.map(c => (
                <tr key={c.id}>
                  <td className="font-black text-blue-600">{c.codigo}</td>
                  <td>{c.nombre}</td>
                  <td>{c.empresa_nombre}</td>
                  <td>{c.tipo.replace('_', ' ')}</td>
                  <td>{c.horas_incluidas_mes ? `${c.horas_consumidas_mes}/${c.horas_incluidas_mes}h` : '—'}</td>
                  <td className={c.dias_para_vencer !== null && c.dias_para_vencer !== undefined && c.dias_para_vencer < 30 ? 'font-bold text-rose-600' : ''}>
                    {c.fecha_fin || 'Indefinido'}
                    {c.dias_para_vencer !== null && c.dias_para_vencer !== undefined && c.dias_para_vencer < 30 && c.estado === 'VIGENTE' && (
                      <span className="ml-1 inline-flex items-center gap-1 text-xs"><AlertTriangle size={12} />{c.dias_para_vencer}d</span>
                    )}
                  </td>
                  <td><span className={`badge ${ESTADO_COLOR[c.estado]}`}>{c.estado}</span></td>
                  <td>
                    <div className="flex gap-1.5">
                      <button className="btn-secondary !px-2.5 !py-1 text-xs" onClick={() => openEdit(c)}>Editar</button>
                      {c.estado === 'VIGENTE' && <button className="btn-secondary !px-2.5 !py-1 text-xs" onClick={() => cambiarEstado.mutate({id: c.id, estado: 'CANCELADO'})}>Cancelar</button>}
                    </div>
                  </td>
                </tr>
              ))}
              {contratos.length === 0 && <tr><td colSpan={8} className="py-8 text-center text-slate-400">No hay contratos registrados</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={open} title={editing ? 'Editar contrato' : 'Nuevo contrato'} onClose={() => {setOpen(false); setEditing(null)}}>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); editing ? actualizar.mutate() : crear.mutate()}}>
          {!editing && (
            <label className="sm:col-span-2"><span className="label">Empresa</span>
              <select className="field" required value={form.empresa_id} onChange={e => setForm({...form, empresa_id: e.target.value})}>
                <option value="">Selecciona una empresa</option>
                {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
              </select>
            </label>
          )}
          <label className="sm:col-span-2"><span className="label">Nombre del contrato</span><input className="field" required value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} /></label>
          <label><span className="label">Tipo</span>
            <select className="field" value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})}>
              {TIPOS.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
            </select>
          </label>
          <label><span className="label">Horas incluidas / mes</span><input type="number" min={0} className="field" value={form.horas_incluidas_mes} onChange={e => setForm({...form, horas_incluidas_mes: e.target.value})} /></label>
          <label><span className="label">Fecha de inicio</span><input type="date" className="field" required value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} /></label>
          <label><span className="label">Fecha de fin (opcional)</span><input type="date" className="field" value={form.fecha_fin} onChange={e => setForm({...form, fecha_fin: e.target.value})} /></label>
          <label><span className="label">Valor mensual (S/)</span><input type="number" min={0} className="field" value={form.valor_mensual} onChange={e => setForm({...form, valor_mensual: e.target.value})} /></label>
          <label className="sm:col-span-2"><span className="label">Notas</span><textarea className="field" rows={3} value={form.notas} onChange={e => setForm({...form, notas: e.target.value})} /></label>
          <div className="sm:col-span-2 flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => {setOpen(false); setEditing(null)}}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending || actualizar.isPending}>{editing ? 'Guardar cambios' : 'Crear contrato'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
