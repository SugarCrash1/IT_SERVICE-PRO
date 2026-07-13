import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {CheckCircle2, Plus, Trash2, Truck, XCircle} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {Company, DeliveryNote} from '../types';

const TIPOS = ['ENTREGA_EQUIPO', 'INSTALACION', 'PRESTAMO', 'DEVOLUCION', 'TRASLADO_INTERNO'];
const ESTADO_COLOR: Record<string, string> = {
  EMITIDA: 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300',
  ENTREGADA: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  ANULADA: 'bg-slate-200 text-slate-600 dark:bg-slate-800',
};

type Linea = {producto_id: string; cantidad: number; descripcion: string};

export function DeliveryNotesPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [empresaId, setEmpresaId] = useState('');
  const [tipo, setTipo] = useState('ENTREGA_EQUIPO');
  const [direccion, setDireccion] = useState('');
  const [transportista, setTransportista] = useState('');
  const [lineas, setLineas] = useState<Linea[]>([{producto_id: '', cantidad: 1, descripcion: ''}]);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: productos = []} = useQuery({queryKey: ['products-all'], queryFn: async () => (await http.get('/products', {params: {tamano_pagina: 200}})).data.items});
  const {data: guias = [], isLoading} = useQuery({queryKey: ['delivery-notes'], queryFn: async () => (await http.get('/delivery-notes')).data as DeliveryNote[]});

  const invalidate = () => qc.invalidateQueries({queryKey: ['delivery-notes']});
  const crear = useMutation({
    mutationFn: () => http.post('/delivery-notes', {
      empresa_id: empresaId, tipo, direccion_entrega: direccion || undefined, transportista: transportista || undefined,
      detalles: lineas.filter(l => l.producto_id && l.cantidad > 0).map(l => ({producto_id: l.producto_id, cantidad: l.cantidad, descripcion: l.descripcion || undefined})),
    }),
    onSuccess: () => {toast.success('Guía emitida'); setOpen(false); setLineas([{producto_id: '', cantidad: 1, descripcion: ''}]); setEmpresaId(''); setDireccion(''); setTransportista(''); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const entregar = useMutation({
    mutationFn: (id: string) => http.post(`/delivery-notes/${id}/deliver`),
    onSuccess: () => {toast.success('Entrega confirmada, stock actualizado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });
  const anular = useMutation({
    mutationFn: (id: string) => http.post(`/delivery-notes/${id}/void`),
    onSuccess: () => {toast.success('Guía anulada'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  const setLinea = (i: number, campo: keyof Linea, valor: string | number) => {
    setLineas(ls => ls.map((l, idx) => idx === i ? {...l, [campo]: valor} : l));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><Truck className="text-blue-600" />Guías de remisión</h1>
          <p className="text-slate-500">Despacho de equipos y materiales hacia empresas cliente.</p>
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}><Plus size={17} />Nueva guía</button>
      </div>

      {isLoading ? <div className="card">Cargando guías...</div> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>N°</th><th>Empresa</th><th>Tipo</th><th>Productos</th><th>Fecha</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {guias.map(g => (
                <tr key={g.id}>
                  <td className="font-black text-blue-600">{g.numero}</td>
                  <td>{g.empresa_nombre}</td>
                  <td>{g.tipo.replace(/_/g, ' ')}</td>
                  <td>{g.detalles.map(d => `${d.cantidad}× ${d.producto_nombre}`).join(', ')}</td>
                  <td>{g.fecha_emision}</td>
                  <td><span className={`badge ${ESTADO_COLOR[g.estado]}`}>{g.estado}</span></td>
                  <td>
                    {g.estado === 'EMITIDA' && (
                      <div className="flex gap-1.5">
                        <button className="btn-secondary !px-2.5 !py-1 text-xs" onClick={() => entregar.mutate(g.id)}><CheckCircle2 size={13} className="mr-1 inline" />Confirmar entrega</button>
                        <button className="btn-secondary !px-2.5 !py-1 text-xs text-rose-600" onClick={() => anular.mutate(g.id)}><XCircle size={13} /></button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {guias.length === 0 && <tr><td colSpan={7} className="py-8 text-center text-slate-400">No hay guías registradas</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={open} title="Nueva guía de remisión" onClose={() => setOpen(false)}>
        <form className="space-y-4" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
          <label><span className="label">Empresa destino</span>
            <select className="field" required value={empresaId} onChange={e => setEmpresaId(e.target.value)}>
              <option value="">Selecciona una empresa</option>
              {empresas.map((e: Company) => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
            </select>
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label><span className="label">Tipo</span>
              <select className="field" value={tipo} onChange={e => setTipo(e.target.value)}>
                {TIPOS.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
              </select>
            </label>
            <label><span className="label">Transportista (opcional)</span><input className="field" value={transportista} onChange={e => setTransportista(e.target.value)} /></label>
          </div>
          <label><span className="label">Dirección de entrega (opcional)</span><input className="field" value={direccion} onChange={e => setDireccion(e.target.value)} /></label>

          <div>
            <span className="label">Productos a despachar</span>
            <div className="mt-2 space-y-2">
              {lineas.map((l, i) => (
                <div key={i} className="flex gap-2">
                  <select className="field flex-1" value={l.producto_id} onChange={e => setLinea(i, 'producto_id', e.target.value)}>
                    <option value="">Selecciona un producto</option>
                    {productos.map((p: any) => <option key={p.id} value={p.id}>{p.nombre} (stock: {p.stock})</option>)}
                  </select>
                  <input type="number" min={1} className="field w-24" value={l.cantidad} onChange={e => setLinea(i, 'cantidad', Number(e.target.value))} />
                  {lineas.length > 1 && <button type="button" className="btn-secondary !px-3" onClick={() => setLineas(ls => ls.filter((_, idx) => idx !== i))}><Trash2 size={14} /></button>}
                </div>
              ))}
            </div>
            <button type="button" className="btn-secondary mt-2 !px-3 !py-1.5 text-xs" onClick={() => setLineas(ls => [...ls, {producto_id: '', cantidad: 1, descripcion: ''}])}><Plus size={13} className="mr-1 inline" />Agregar producto</button>
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending}>Emitir guía</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
