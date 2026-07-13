import {useQuery} from '@tanstack/react-query';
import {Building2, Globe2, Mail, Phone, ShieldCheck, Star, UserRound} from 'lucide-react';
import {http} from '../api/http';

export function ClientCompanyPage() {
  const {data, isLoading} = useQuery({
    queryKey: ['client-company'],
    queryFn: async () => (await http.get('/client-portal/company')).data.data as {
      empresa: {razon_social: string; nombre_comercial?: string; ruc: string; sector?: string; nivel_sla: string; ciudad?: string; telefono?: string; correo?: string; contrato_fin?: string};
      mi_contacto: {nombres: string; apellidos: string; cargo?: string; correo: string; es_contacto_principal: boolean};
      contactos: {id: string; nombres: string; apellidos: string; cargo?: string; correo: string; es_contacto_principal: boolean}[];
    },
  });

  if (isLoading || !data) return <div className="card">Cargando información de tu empresa...</div>;
  const {empresa, mi_contacto, contactos} = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title flex items-center gap-2"><Building2 className="text-blue-600" />Mi empresa</h1>
        <p className="text-slate-500">Información corporativa y contactos autorizados.</p>
      </div>

      <div className="card">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-xl font-black">{empresa.nombre_comercial || empresa.razon_social}</h2>
            <p className="text-sm text-slate-500">{empresa.razon_social} · RUC {empresa.ruc}</p>
          </div>
          <span className="badge bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300"><ShieldCheck size={13} className="mr-1 inline" />SLA {empresa.nivel_sla}</span>
        </div>
        <div className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
          {empresa.sector && <p>Sector: {empresa.sector}</p>}
          {empresa.ciudad && <p className="flex items-center gap-2"><Globe2 size={14} className="text-slate-400" />{empresa.ciudad}</p>}
          {empresa.telefono && <p className="flex items-center gap-2"><Phone size={14} className="text-slate-400" />{empresa.telefono}</p>}
          {empresa.correo && <p className="flex items-center gap-2"><Mail size={14} className="text-slate-400" />{empresa.correo}</p>}
          {empresa.contrato_fin && <p>Contrato vigente hasta: {empresa.contrato_fin}</p>}
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-black text-slate-500">Contactos autorizados</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          {contactos.map(c => (
            <article key={c.id} className="card">
              <div className="flex items-center justify-between gap-2">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/50"><UserRound size={18} /></div>
                {c.es_contacto_principal && <Star size={16} className="text-amber-500" />}
              </div>
              <h4 className="mt-2 font-bold">{c.nombres} {c.apellidos}{c.correo === mi_contacto.correo && <span className="ml-2 text-xs font-normal text-blue-600">(tú)</span>}</h4>
              <p className="text-sm text-slate-500">{c.cargo || 'Sin cargo'}</p>
              <p className="mt-1 flex items-center gap-2 text-xs text-slate-400"><Mail size={12} />{c.correo}</p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
