import {useQuery} from '@tanstack/react-query';
import {AlertTriangle, Server} from 'lucide-react';
import {http} from '../api/http';
import type {Asset} from '../types';

export function ClientAssetsPage() {
  const {data: activos = [], isLoading} = useQuery({
    queryKey: ['client-assets'],
    queryFn: async () => (await http.get('/client-portal/assets')).data.data as Asset[],
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title flex items-center gap-2"><Server className="text-blue-600" />Mis activos</h1>
        <p className="text-slate-500">Equipos, licencias y servidores que administramos para tu empresa.</p>
      </div>

      {isLoading ? (
        <div className="card">Cargando activos...</div>
      ) : activos.length === 0 ? (
        <div className="card text-center text-slate-500">Aún no hay activos registrados para tu empresa.</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {activos.map(a => (
            <article className="card" key={a.id}>
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-black text-blue-600">{a.codigo}</span>
                <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-800">{a.tipo}</span>
              </div>
              <h2 className="mt-2 font-bold">{a.nombre}</h2>
              <p className="text-sm text-slate-500">{[a.marca, a.modelo].filter(Boolean).join(' · ') || 'Sin detalle de marca/modelo'}</p>
              {a.ubicacion && <p className="mt-1 text-xs text-slate-400">Ubicación: {a.ubicacion}</p>}
              {a.fecha_garantia_fin && (
                <p className={`mt-2 text-xs font-semibold ${a.garantia_vencida ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {a.garantia_vencida ? <span className="inline-flex items-center gap-1"><AlertTriangle size={12} />Garantía vencida ({a.fecha_garantia_fin})</span> : `Garantía vigente hasta ${a.fecha_garantia_fin}`}
                </p>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
