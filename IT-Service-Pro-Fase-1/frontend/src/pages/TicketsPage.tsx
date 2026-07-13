import {useMemo, useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  AlertTriangle, Building2, CheckCircle2, Clock3, Loader2, MessageSquare,
  Paperclip, Plus, Search, Send, Ticket as TicketIcon, TimerReset, UserCog,
} from 'lucide-react';
import {http, errorMessage, fileUrl} from '../api/http';
import {Modal} from '../components/Modal';
import {useAuth} from '../auth/AuthContext';
import type {Company, Contact, Employee, ITService, Ticket, TicketListItem, TicketSummary} from '../types';

const ESTADOS = ['ABIERTO', 'EN_PROGRESO', 'EN_ESPERA_CLIENTE', 'EN_ESPERA_TERCERO', 'RESUELTO', 'CERRADO', 'CANCELADO'];
const PRIORIDADES = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA'];
const CATEGORIAS = ['INCIDENTE', 'REQUERIMIENTO', 'CONSULTA', 'CAMBIO', 'PROBLEMA'];
const CANALES = ['INTERNO', 'PORTAL', 'CORREO', 'TELEFONO', 'CHAT', 'PRESENCIAL'];

const ESTADO_LABEL: Record<string, string> = {
  ABIERTO: 'Abierto', EN_PROGRESO: 'En progreso', EN_ESPERA_CLIENTE: 'Espera cliente',
  EN_ESPERA_TERCERO: 'Espera tercero', RESUELTO: 'Resuelto', CERRADO: 'Cerrado', CANCELADO: 'Cancelado',
};
const ESTADO_COLOR: Record<string, string> = {
  ABIERTO: 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300',
  EN_PROGRESO: 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300',
  EN_ESPERA_CLIENTE: 'bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300',
  EN_ESPERA_TERCERO: 'bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300',
  RESUELTO: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300',
  CERRADO: 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
  CANCELADO: 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300',
};
const PRIORIDAD_COLOR: Record<string, string> = {
  BAJA: 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
  MEDIA: 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300',
  ALTA: 'bg-orange-100 text-orange-700 dark:bg-orange-950/50 dark:text-orange-300',
  CRITICA: 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300',
};
const TRANSICIONES: Record<string, string[]> = {
  ABIERTO: ['EN_PROGRESO', 'EN_ESPERA_CLIENTE', 'EN_ESPERA_TERCERO', 'CANCELADO'],
  EN_PROGRESO: ['EN_ESPERA_CLIENTE', 'EN_ESPERA_TERCERO', 'RESUELTO', 'CANCELADO'],
  EN_ESPERA_CLIENTE: ['EN_PROGRESO', 'RESUELTO', 'CANCELADO'],
  EN_ESPERA_TERCERO: ['EN_PROGRESO', 'RESUELTO', 'CANCELADO'],
  RESUELTO: ['CERRADO', 'EN_PROGRESO'],
  CERRADO: [], CANCELADO: [],
};

function fmt(d?: string | null) {
  if (!d) return '—';
  return new Date(d).toLocaleString('es-PE', {day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'});
}

function Badge({text, className}: {text: string; className: string}) {
  return <span className={`badge ${className}`}>{text}</span>;
}

export function TicketsPage({board = false}: {board?: boolean}) {
  const {user} = useAuth();
  const qc = useQueryClient();
  const esTecnico = user?.rol === 'TECNICO';
  const puedeCrear = user?.rol === 'ADMINISTRADOR' || user?.rol === 'COORDINADOR';

  const [busqueda, setBusqueda] = useState('');
  const [estado, setEstado] = useState('');
  const [prioridad, setPrioridad] = useState('');
  const [soloVencidos, setSoloVencidos] = useState(false);
  const [soloMios, setSoloMios] = useState(false);
  const [openCreate, setOpenCreate] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const params = {
    busqueda: busqueda || undefined, estado: estado || undefined, prioridad: prioridad || undefined,
    solo_vencidos: soloVencidos || undefined, solo_mis_tickets: soloMios || undefined, tamano_pagina: 100,
  };
  const {data: listData, isLoading} = useQuery({
    queryKey: ['tickets', params],
    queryFn: async () => (await http.get('/tickets', {params})).data as {items: TicketListItem[]; total: number},
    refetchInterval: 30000,
  });
  const {data: summary} = useQuery({
    queryKey: ['tickets-summary', soloMios],
    queryFn: async () => (await http.get('/tickets/summary', {params: {solo_mis_tickets: soloMios}})).data.data as TicketSummary,
    refetchInterval: 30000,
  });

  const items = listData?.items ?? [];
  const grouped = useMemo(() => {
    const g: Record<string, TicketListItem[]> = {};
    for (const e of ESTADOS) g[e] = [];
    for (const t of items) (g[t.estado] ??= []).push(t);
    return g;
  }, [items]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title">{board ? 'Mesa de ayuda' : 'Tickets'}</h1>
          <p className="text-slate-500">{board ? 'Bandeja operativa por estado para clasificar y asignar.' : 'Motor de solicitudes, incidentes y SLA por empresa.'}</p>
        </div>
        {puedeCrear && (
          <button className="btn-primary" onClick={() => setOpenCreate(true)}><Plus size={17} />Nuevo ticket</button>
        )}
      </div>

      {summary && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <SummaryCard icon={TicketIcon} label="Total" value={summary.total} note="Todos los estados" />
          <SummaryCard icon={Clock3} label="Abiertos" value={(summary.por_estado.ABIERTO || 0) + (summary.por_estado.EN_PROGRESO || 0)} note="Activos ahora" />
          <SummaryCard icon={AlertTriangle} label="Vencidos SLA" value={summary.vencidos} note="Requieren atención" tone="danger" />
          <SummaryCard icon={UserCog} label="Sin asignar" value={summary.sin_asignar} note="Pendientes de asignación" />
          <SummaryCard icon={CheckCircle2} label="Resueltos (mes)" value={summary.resueltos_mes} note={summary.tiempo_promedio_resolucion_horas ? `Prom. ${summary.tiempo_promedio_resolucion_horas}h` : 'Sin datos'} />
        </div>
      )}

      <div className="card space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="absolute left-3 top-3 text-slate-400" size={18} />
            <input className="field pl-10" placeholder="Buscar por código, título o empresa" value={busqueda} onChange={e => setBusqueda(e.target.value)} />
          </div>
          <select className="field w-auto" value={estado} onChange={e => setEstado(e.target.value)}>
            <option value="">Todos los estados</option>
            {ESTADOS.map(e => <option key={e} value={e}>{ESTADO_LABEL[e]}</option>)}
          </select>
          <select className="field w-auto" value={prioridad} onChange={e => setPrioridad(e.target.value)}>
            <option value="">Toda prioridad</option>
            {PRIORIDADES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <label className="flex items-center gap-2 text-sm font-semibold">
            <input type="checkbox" checked={soloVencidos} onChange={e => setSoloVencidos(e.target.checked)} />Solo vencidos
          </label>
          {esTecnico && (
            <label className="flex items-center gap-2 text-sm font-semibold">
              <input type="checkbox" checked={soloMios} onChange={e => setSoloMios(e.target.checked)} />Solo mis tickets
            </label>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="card flex items-center gap-2"><Loader2 className="animate-spin" size={18} />Cargando tickets...</div>
      ) : board ? (
        <div className="grid gap-4 lg:grid-cols-4 xl:grid-cols-4">
          {['ABIERTO', 'EN_PROGRESO', 'EN_ESPERA_CLIENTE', 'RESUELTO'].map(col => (
            <div key={col} className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-sm font-black uppercase tracking-wide text-slate-500">{ESTADO_LABEL[col]}</h3>
                <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-800">{grouped[col]?.length ?? 0}</span>
              </div>
              <div className="space-y-3">
                {(grouped[col] ?? []).map(t => (
                  <button key={t.id} onClick={() => setSelectedId(t.id)} className="card w-full text-left hover:-translate-y-0.5 hover:shadow-lg transition">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-black text-blue-600">{t.codigo}</span>
                      <Badge text={t.prioridad} className={PRIORIDAD_COLOR[t.prioridad]} />
                    </div>
                    <p className="mt-2 line-clamp-2 text-sm font-bold">{t.titulo}</p>
                    <p className="mt-1 flex items-center gap-1 text-xs text-slate-500"><Building2 size={12} />{t.empresa_nombre}</p>
                    {t.vencido && <p className="mt-2 flex items-center gap-1 text-xs font-bold text-rose-600"><AlertTriangle size={12} />SLA vencido</p>}
                  </button>
                ))}
                {(grouped[col] ?? []).length === 0 && <div className="card text-center text-xs text-slate-400">Sin tickets</div>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Código</th><th>Empresa</th><th>Título</th><th>Prioridad</th><th>Estado</th><th>Técnico</th><th>Vence resolución</th><th></th></tr></thead>
            <tbody>
              {items.map(t => (
                <tr key={t.id} className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900/60" onClick={() => setSelectedId(t.id)}>
                  <td className="font-black text-blue-600">{t.codigo}</td>
                  <td>{t.empresa_nombre}</td>
                  <td className="max-w-xs truncate">{t.titulo}</td>
                  <td><Badge text={t.prioridad} className={PRIORIDAD_COLOR[t.prioridad]} /></td>
                  <td><Badge text={ESTADO_LABEL[t.estado]} className={ESTADO_COLOR[t.estado]} /></td>
                  <td>{t.tecnico_nombre || <span className="text-slate-400">Sin asignar</span>}</td>
                  <td className={t.vencido ? 'font-bold text-rose-600' : ''}>{fmt(t.fecha_limite_resolucion)}</td>
                  <td><button className="btn-secondary !px-3 !py-1.5" onClick={e => {e.stopPropagation(); setSelectedId(t.id)}}>Ver</button></td>
                </tr>
              ))}
              {items.length === 0 && <tr><td colSpan={8} className="py-8 text-center text-slate-400">No hay tickets con estos filtros</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {openCreate && <CreateTicketModal onClose={() => setOpenCreate(false)} onCreated={() => {qc.invalidateQueries({queryKey: ['tickets']}); qc.invalidateQueries({queryKey: ['tickets-summary']})}} />}
      {selectedId && <TicketDetailModal id={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  );
}

function SummaryCard({icon: Icon, label, value, note, tone}: {icon: any; label: string; value: number; note: string; tone?: 'danger'}) {
  return (
    <article className="card">
      <div className={`mb-3 grid h-10 w-10 place-items-center rounded-xl ${tone === 'danger' ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300' : 'bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300'}`}><Icon size={18} /></div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-black">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{note}</p>
    </article>
  );
}

function CreateTicketModal({onClose, onCreated}: {onClose: () => void; onCreated: () => void}) {
  const [empresaId, setEmpresaId] = useState('');
  const [form, setForm] = useState({contacto_id: '', servicio_id: '', asignado_a: '', titulo: '', descripcion: '', categoria: 'INCIDENTE', prioridad: 'MEDIA', canal: 'INTERNO'});

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: contactos = []} = useQuery({queryKey: ['itsp-contacts', empresaId], queryFn: async () => empresaId ? (await http.get('/itsp/contacts', {params: {empresa_id: empresaId}})).data as Contact[] : [], enabled: !!empresaId});
  const {data: servicios = []} = useQuery({queryKey: ['itsp-services-all'], queryFn: async () => (await http.get('/itsp/services')).data as ITService[]});
  const {data: tecnicos = []} = useQuery({queryKey: ['employees-all'], queryFn: async () => (await http.get('/employees', {params: {tamano_pagina: 100, estado: 'ACTIVO'}})).data.items as Employee[]});

  const crear = useMutation({
    mutationFn: () => http.post('/tickets', {
      empresa_id: empresaId, contacto_id: form.contacto_id || undefined, servicio_id: form.servicio_id || undefined,
      asignado_a: form.asignado_a || undefined, titulo: form.titulo, descripcion: form.descripcion,
      categoria: form.categoria, prioridad: form.prioridad, canal: form.canal,
    }),
    onSuccess: () => {toast.success('Ticket creado'); onCreated(); onClose()},
    onError: e => toast.error(errorMessage(e)),
  });

  return (
    <Modal open title="Nuevo ticket" onClose={onClose}>
      <form className="grid gap-4 sm:grid-cols-2" onSubmit={e => {e.preventDefault(); if (!empresaId) {toast.error('Selecciona una empresa'); return} crear.mutate()}}>
        <label className="sm:col-span-2"><span className="label">Empresa</span>
          <select className="field" required value={empresaId} onChange={e => {setEmpresaId(e.target.value); setForm(f => ({...f, contacto_id: ''}))}}>
            <option value="">Selecciona una empresa</option>
            {empresas.map(c => <option key={c.id} value={c.id}>{c.nombre_comercial || c.razon_social}</option>)}
          </select>
        </label>
        <label><span className="label">Contacto (opcional)</span>
          <select className="field" value={form.contacto_id} onChange={e => setForm({...form, contacto_id: e.target.value})} disabled={!empresaId}>
            <option value="">Sin contacto específico</option>
            {contactos.map(c => <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>)}
          </select>
        </label>
        <label><span className="label">Servicio TI (opcional)</span>
          <select className="field" value={form.servicio_id} onChange={e => setForm({...form, servicio_id: e.target.value})}>
            <option value="">Sin servicio específico</option>
            {servicios.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </label>
        <label><span className="label">Categoría</span>
          <select className="field" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})}>
            {CATEGORIAS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
        <label><span className="label">Prioridad</span>
          <select className="field" value={form.prioridad} onChange={e => setForm({...form, prioridad: e.target.value})}>
            {PRIORIDADES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        <label><span className="label">Canal</span>
          <select className="field" value={form.canal} onChange={e => setForm({...form, canal: e.target.value})}>
            {CANALES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
        <label><span className="label">Asignar a técnico (opcional)</span>
          <select className="field" value={form.asignado_a} onChange={e => setForm({...form, asignado_a: e.target.value})}>
            <option value="">Sin asignar</option>
            {tecnicos.map(t => <option key={t.id} value={t.id}>{t.nombre_completo}</option>)}
          </select>
        </label>
        <label className="sm:col-span-2"><span className="label">Título</span>
          <input className="field" required maxLength={200} value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} />
        </label>
        <label className="sm:col-span-2"><span className="label">Descripción</span>
          <textarea className="field" required rows={4} value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} />
        </label>
        <div className="sm:col-span-2 flex justify-end gap-2">
          <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn-primary" disabled={crear.isPending}>{crear.isPending ? 'Creando...' : 'Crear ticket'}</button>
        </div>
      </form>
    </Modal>
  );
}

export function TicketDetailModal({id, onClose, portal = false}: {id: string; onClose: () => void; portal?: boolean}) {
  const {user} = useAuth();
  const qc = useQueryClient();
  const base = portal ? '/client-portal/tickets' : '/tickets';
  const [comentario, setComentario] = useState('');
  const [esInterno, setEsInterno] = useState(false);
  const [subiendo, setSubiendo] = useState(false);

  const {data, isLoading} = useQuery({
    queryKey: ['ticket', base, id],
    queryFn: async () => (await http.get(`${base}/${id}`)).data.data as Ticket,
    refetchInterval: 15000,
  });
  const {data: tecnicos = []} = useQuery({
    queryKey: ['employees-all'], queryFn: async () => (await http.get('/employees', {params: {tamano_pagina: 100, estado: 'ACTIVO'}})).data.items as Employee[],
    enabled: !portal,
  });

  const invalidate = () => {qc.invalidateQueries({queryKey: ['ticket', base, id]}); qc.invalidateQueries({queryKey: ['tickets']}); qc.invalidateQueries({queryKey: ['tickets-summary']})};

  const comentar = useMutation({
    mutationFn: () => http.post(`${base}/${id}/comments`, {contenido: comentario, es_interno: esInterno}),
    onSuccess: () => {setComentario(''); setEsInterno(false); invalidate(); toast.success('Comentario agregado')},
    onError: e => toast.error(errorMessage(e)),
  });
  const cambiarEstado = useMutation({
    mutationFn: (estado: string) => http.patch(`/tickets/${id}/status`, {estado, motivo_cierre: estado === 'CANCELADO' ? prompt('Motivo de cancelación:') || 'Sin especificar' : undefined}),
    onSuccess: () => {invalidate(); toast.success('Estado actualizado')},
    onError: e => toast.error(errorMessage(e)),
  });
  const asignar = useMutation({
    mutationFn: (empleado_id: string) => http.patch(`/tickets/${id}/assign`, {empleado_id}),
    onSuccess: () => {invalidate(); toast.success('Ticket asignado')},
    onError: e => toast.error(errorMessage(e)),
  });
  const registrarTiempo = useMutation({
    mutationFn: (minutos: number) => http.post(`/tickets/${id}/time-log`, {minutos}),
    onSuccess: () => {invalidate(); toast.success('Tiempo registrado')},
    onError: e => toast.error(errorMessage(e)),
  });
  const calificar = useMutation({
    mutationFn: (calificacion: number) => http.post(`${base}/${id}/satisfaction`, {calificacion}),
    onSuccess: () => {invalidate(); toast.success('¡Gracias por tu calificación!')},
    onError: e => toast.error(errorMessage(e)),
  });
  const adjuntar = useMutation({
    mutationFn: async (archivo: File) => {
      const form = new FormData();
      form.append('archivo', archivo);
      const subida = await http.post('/uploads', form, {headers: {'Content-Type': undefined}});
      const {url, nombre_archivo, tipo_mime, tamano_bytes} = subida.data.data;
      return http.post(`${base}/${id}/attachments`, {url_archivo: url, nombre_archivo, tipo_mime, tamano_bytes});
    },
    onMutate: () => setSubiendo(true),
    onSuccess: () => {invalidate(); toast.success('Archivo adjuntado')},
    onError: e => toast.error(errorMessage(e)),
    onSettled: () => setSubiendo(false),
  });

  if (isLoading || !data) {
    return <Modal open title="Ticket" onClose={onClose}><div className="flex items-center gap-2 py-8 justify-center text-slate-500"><Loader2 className="animate-spin" size={18} />Cargando...</div></Modal>;
  }

  const puedeGestionar = !portal && (user?.rol === 'ADMINISTRADOR' || user?.rol === 'COORDINADOR' || user?.rol === 'TECNICO');
  const puedeAsignar = !portal && (user?.rol === 'ADMINISTRADOR' || user?.rol === 'COORDINADOR');

  return (
    <Modal open title={`${data.codigo} · ${data.titulo}`} onClose={onClose}>
      <div className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge text={ESTADO_LABEL[data.estado]} className={ESTADO_COLOR[data.estado]} />
          <Badge text={data.prioridad} className={PRIORIDAD_COLOR[data.prioridad]} />
          <Badge text={data.categoria} className="bg-slate-100 text-slate-600 dark:bg-slate-800" />
          {data.vencido && <Badge text="SLA vencido" className="bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300" />}
        </div>

        <div className="grid gap-3 sm:grid-cols-2 text-sm">
          <p className="flex items-center gap-2"><Building2 size={14} className="text-slate-400" />{data.empresa_nombre}{data.contacto_nombre ? ` · ${data.contacto_nombre}` : ''}</p>
          <p className="flex items-center gap-2"><UserCog size={14} className="text-slate-400" />{data.tecnico_nombre || 'Sin asignar'}</p>
          <p className="flex items-center gap-2"><Clock3 size={14} className="text-slate-400" />Respuesta límite: {fmt(data.fecha_limite_respuesta)}</p>
          <p className="flex items-center gap-2"><TimerReset size={14} className="text-slate-400" />Resolución límite: {fmt(data.fecha_limite_resolucion)}</p>
        </div>

        <div className="rounded-2xl border border-slate-200 p-4 text-sm dark:border-slate-800">{data.descripcion}</div>

        {puedeGestionar && (
          <div className="flex flex-wrap items-center gap-2">
            {(TRANSICIONES[data.estado] || []).map(next => (
              <button key={next} className="btn-secondary !px-3 !py-1.5 text-xs" disabled={cambiarEstado.isPending} onClick={() => cambiarEstado.mutate(next)}>
                → {ESTADO_LABEL[next]}
              </button>
            ))}
            {puedeAsignar && (
              <select className="field !w-auto !py-1.5 text-xs" value={data.tecnico_id || ''} onChange={e => e.target.value && asignar.mutate(e.target.value)}>
                <option value="">Reasignar técnico...</option>
                {tecnicos.map(t => <option key={t.id} value={t.id}>{t.nombre_completo}</option>)}
              </select>
            )}
            <button className="btn-secondary !px-3 !py-1.5 text-xs" onClick={() => {const m = prompt('Minutos invertidos:'); const n = m ? parseInt(m, 10) : 0; if (n > 0) registrarTiempo.mutate(n)}}>
              <Clock3 size={13} className="inline mr-1" />Registrar tiempo ({data.tiempo_invertido_minutos}m)
            </button>
          </div>
        )}

        {portal && (data.estado === 'RESUELTO' || data.estado === 'CERRADO') && !data.calificacion_satisfaccion && (
          <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950/30">
            <p className="text-sm font-bold">¿Cómo calificarías la atención recibida?</p>
            <div className="mt-2 flex gap-2">
              {[1, 2, 3, 4, 5].map(n => <button key={n} className="btn-secondary !px-3 !py-1.5" onClick={() => calificar.mutate(n)}>{n}★</button>)}
            </div>
          </div>
        )}
        {data.calificacion_satisfaccion && (
          <p className="text-sm font-semibold text-emerald-600">Calificación del cliente: {data.calificacion_satisfaccion}/5 ★</p>
        )}

        <div>
          <h3 className="flex items-center gap-2 text-sm font-black"><Paperclip size={15} />Adjuntos ({data.adjuntos.length})</h3>
          <div className="mt-2 flex flex-wrap gap-3">
            {data.adjuntos.map(a => {
              const esImagen = /\.(jpe?g|png|webp|gif|heic)$/i.test(a.nombre_archivo);
              return (
                <a key={a.id} href={fileUrl(a.url_archivo)} target="_blank" rel="noreferrer" className="group block w-24 text-center">
                  {esImagen ? (
                    <img src={fileUrl(a.url_archivo)} alt={a.nombre_archivo} className="h-24 w-24 rounded-xl border border-slate-200 object-cover dark:border-slate-800" />
                  ) : (
                    <div className="grid h-24 w-24 place-items-center rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800"><Paperclip size={22} className="text-slate-400" /></div>
                  )}
                  <p className="mt-1 truncate text-xs text-slate-500 group-hover:text-blue-600">{a.nombre_archivo}</p>
                </a>
              );
            })}
            {data.estado !== 'CERRADO' && data.estado !== 'CANCELADO' && (
              <label className="grid h-24 w-24 cursor-pointer place-items-center rounded-xl border-2 border-dashed border-slate-300 text-slate-400 hover:border-blue-400 hover:text-blue-500 dark:border-slate-700">
                {subiendo ? <Loader2 size={20} className="animate-spin" /> : <Plus size={20} />}
                <input type="file" className="hidden" accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.zip" disabled={subiendo}
                  onChange={e => {const f = e.target.files?.[0]; if (f) adjuntar.mutate(f); e.target.value = ''}} />
              </label>
            )}
          </div>
        </div>

        <div>
          <h3 className="flex items-center gap-2 text-sm font-black"><MessageSquare size={15} />Conversación</h3>
          <div className="mt-3 max-h-72 space-y-3 overflow-y-auto pr-1">
            {data.comentarios.length === 0 && <p className="text-sm text-slate-400">Aún no hay comentarios.</p>}
            {data.comentarios.map(c => (
              <div key={c.id} className={`rounded-2xl p-3 text-sm ${c.es_interno ? 'border border-dashed border-amber-300 bg-amber-50 dark:bg-amber-950/20' : c.es_del_cliente ? 'bg-blue-50 dark:bg-blue-950/30' : 'bg-slate-100 dark:bg-slate-800'}`}>
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="font-bold">{c.autor_nombre}{c.es_interno ? ' · nota interna' : ''}</span>
                  <span className="text-xs text-slate-400">{fmt(c.created_at)}</span>
                </div>
                <p className="whitespace-pre-wrap">{c.contenido}</p>
              </div>
            ))}
          </div>
          {data.estado !== 'CERRADO' && data.estado !== 'CANCELADO' && (
            <form className="mt-3 space-y-2" onSubmit={e => {e.preventDefault(); if (comentario.trim()) comentar.mutate()}}>
              <textarea className="field" rows={3} placeholder="Escribe una respuesta..." value={comentario} onChange={e => setComentario(e.target.value)} />
              <div className="flex items-center justify-between">
                {!portal ? (
                  <label className="flex items-center gap-2 text-xs font-semibold"><input type="checkbox" checked={esInterno} onChange={e => setEsInterno(e.target.checked)} />Nota interna (no visible al cliente)</label>
                ) : <span />}
                <button className="btn-primary !px-4 !py-2" disabled={comentar.isPending}><Send size={14} />Enviar</button>
              </div>
            </form>
          )}
        </div>

        {data.historial.length > 0 && (
          <details className="text-sm">
            <summary className="cursor-pointer font-bold text-slate-500">Historial ({data.historial.length})</summary>
            <div className="mt-2 space-y-1.5 border-l-2 border-slate-200 pl-3 dark:border-slate-800">
              {data.historial.map(h => <p key={h.id} className="text-xs text-slate-500"><span className="font-bold text-slate-700 dark:text-slate-300">{fmt(h.created_at)}</span> — {h.descripcion} <span className="text-slate-400">({h.actor_nombre})</span></p>)}
            </div>
          </details>
        )}
      </div>
    </Modal>
  );
}
