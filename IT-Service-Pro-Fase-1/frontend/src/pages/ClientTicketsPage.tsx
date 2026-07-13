import {useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {Link} from 'react-router-dom';
import {AlertTriangle, Search, TicketCheck, TicketPlus} from 'lucide-react';
import {http} from '../api/http';
import type {TicketListItem} from '../types';
import {TicketDetailModal} from './TicketsPage';

const ESTADO_LABEL: Record<string, string> = {
  ABIERTO: 'Abierto', EN_PROGRESO: 'En progreso', EN_ESPERA_CLIENTE: 'Esperando tu respuesta',
  EN_ESPERA_TERCERO: 'En espera', RESUELTO: 'Resuelto', CERRADO: 'Cerrado', CANCELADO: 'Cancelado',
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

export function ClientTicketsPage() {
  const [estado, setEstado] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const {data, isLoading} = useQuery({
    queryKey: ['client-tickets', estado],
    queryFn: async () => (await http.get('/client-portal/tickets', {params: {estado: estado || undefined, tamano_pagina: 100}})).data.data as {items: TicketListItem[]; total: number},
    refetchInterval: 20000,
  });

  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><TicketCheck className="text-blue-600" />Mis tickets</h1>
          <p className="text-slate-500">Seguimiento de las solicitudes registradas por tu empresa.</p>
        </div>
        <Link to="/cliente/crear-ticket" className="btn-primary"><TicketPlus size={17} />Nuevo ticket</Link>
      </div>

      <div className="card flex flex-wrap items-center gap-3">
        <Search className="text-slate-400" size={18} />
        <select className="field w-auto" value={estado} onChange={e => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          {Object.entries(ESTADO_LABEL).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>

      {isLoading ? (
        <div className="card">Cargando tickets...</div>
      ) : items.length === 0 ? (
        <div className="card text-center text-slate-500">Aún no has registrado ningún ticket.
          <Link to="/cliente/crear-ticket" className="btn-primary mt-4 inline-flex"><TicketPlus size={17} />Crear el primero</Link>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map(t => (
            <button key={t.id} onClick={() => setSelectedId(t.id)} className="card text-left hover:-translate-y-0.5 hover:shadow-lg transition">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-black text-blue-600">{t.codigo}</span>
                <span className={`badge ${ESTADO_COLOR[t.estado]}`}>{ESTADO_LABEL[t.estado]}</span>
              </div>
              <h3 className="mt-2 font-bold">{t.titulo}</h3>
              <p className="mt-1 text-xs text-slate-500">Prioridad {t.prioridad.toLowerCase()} · {t.tecnico_nombre ? `Atendido por ${t.tecnico_nombre}` : 'Aún sin asignar'}</p>
              {t.vencido && <p className="mt-2 flex items-center gap-1 text-xs font-bold text-rose-600"><AlertTriangle size={12} />Fuera de SLA</p>}
            </button>
          ))}
        </div>
      )}

      {selectedId && <TicketDetailModal id={selectedId} onClose={() => setSelectedId(null)} portal />}
    </div>
  );
}
