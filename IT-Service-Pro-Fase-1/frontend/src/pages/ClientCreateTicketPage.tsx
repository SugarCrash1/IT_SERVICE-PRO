import {useState} from 'react';
import {useMutation, useQuery} from '@tanstack/react-query';
import {useNavigate} from 'react-router-dom';
import toast from 'react-hot-toast';
import {TicketPlus} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import type {ITService} from '../types';

const CATEGORIAS = [
  ['INCIDENTE', 'Algo dejó de funcionar'],
  ['REQUERIMIENTO', 'Necesito un nuevo recurso o acceso'],
  ['CONSULTA', 'Tengo una pregunta'],
  ['CAMBIO', 'Solicito un cambio planificado'],
  ['PROBLEMA', 'Un incidente recurrente'],
] as const;
const PRIORIDADES = [
  ['BAJA', 'Puede esperar'], ['MEDIA', 'Impacto moderado'],
  ['ALTA', 'Impacto alto, bloquea trabajo'], ['CRITICA', 'Servicio caído / urgente'],
] as const;

export function ClientCreateTicketPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({servicio_id: '', titulo: '', descripcion: '', categoria: 'INCIDENTE', prioridad: 'MEDIA'});

  const {data: servicios = []} = useQuery({
    queryKey: ['client-services-catalog'],
    queryFn: async () => (await http.get('/client-portal/services-catalog')).data.data as ITService[],
  });

  const crear = useMutation({
    mutationFn: () => http.post('/client-portal/tickets', {
      servicio_id: form.servicio_id || undefined, titulo: form.titulo, descripcion: form.descripcion,
      categoria: form.categoria, prioridad: form.prioridad,
    }),
    onSuccess: (r) => {toast.success(`Ticket ${r.data.data.codigo} creado`); navigate('/cliente/mis-tickets')},
    onError: e => toast.error(errorMessage(e)),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="page-title flex items-center gap-2"><TicketPlus className="text-blue-600" />Crear ticket</h1>
        <p className="text-slate-500">Cuéntanos qué necesitas y nuestro equipo te contactará según el SLA de tu contrato.</p>
      </div>
      <form className="card space-y-4" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
        <label><span className="label">¿Qué tipo de solicitud es?</span>
          <select className="field" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})}>
            {CATEGORIAS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>
        <label><span className="label">Prioridad</span>
          <select className="field" value={form.prioridad} onChange={e => setForm({...form, prioridad: e.target.value})}>
            {PRIORIDADES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>
        <label><span className="label">Servicio relacionado (opcional)</span>
          <select className="field" value={form.servicio_id} onChange={e => setForm({...form, servicio_id: e.target.value})}>
            <option value="">No estoy seguro / otro</option>
            {servicios.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </label>
        <label><span className="label">Título</span>
          <input className="field" required maxLength={200} placeholder="Ej. No puedo acceder a mi correo corporativo"
            value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} />
        </label>
        <label><span className="label">Descripción</span>
          <textarea className="field" required rows={6} placeholder="Describe el problema con el mayor detalle posible: qué pasó, desde cuándo, a quién afecta..."
            value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} />
        </label>
        <button className="btn-primary w-full justify-center" disabled={crear.isPending}>{crear.isPending ? 'Enviando...' : 'Enviar ticket'}</button>
      </form>
    </div>
  );
}
