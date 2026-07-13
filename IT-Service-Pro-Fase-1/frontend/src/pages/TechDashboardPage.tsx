import {useQuery} from '@tanstack/react-query';
import {http} from '../api/http';
import {useAuth} from '../auth/AuthContext';
import {AlertTriangle, Building2, CheckCircle2, Clock3, FolderKanban, Server, TicketCheck, UsersRound} from 'lucide-react';

const roleCopy:Record<string,{title:string;subtitle:string}>={
 ADMINISTRADOR:{title:'Dashboard ejecutivo',subtitle:'Visión general de clientes, operación y capacidad tecnológica.'},
 COORDINADOR:{title:'Mesa de ayuda',subtitle:'Prioriza, asigna y controla la operación diaria del Service Desk.'},
 TECNICO:{title:'Mi operación técnica',subtitle:'Gestiona tus tickets, tareas y compromisos de servicio.'},
 CLIENTE:{title:'Portal de servicios',subtitle:'Consulta tus solicitudes y servicios contratados.'},
};
export function TechDashboardPage(){
 const{user}=useAuth();
 const{data}=useQuery({queryKey:['itsp-foundation'],queryFn:async()=> (await http.get('/itsp/foundation')).data});
 const esCliente=user?.rol==='CLIENTE';
 const{data:ticketSummary}=useQuery({queryKey:['tickets-summary-dash'],queryFn:async()=> (await http.get('/tickets/summary')).data.data,enabled:!esCliente});
 const c=roleCopy[user?.rol||'ADMINISTRADOR'];
 const abiertos=(ticketSummary?.por_estado?.ABIERTO||0)+(ticketSummary?.por_estado?.EN_PROGRESO||0);
 const cumplimiento=ticketSummary?.total?Math.max(0,100-(ticketSummary.vencidos/ticketSummary.total*100)).toFixed(1):'—';
 const metrics=[
  [TicketCheck,'Tickets abiertos',ticketSummary?String(abiertos):'—',`${ticketSummary?.por_prioridad?.CRITICA||0} críticos`],
  [AlertTriangle,'Vencidos SLA',ticketSummary?String(ticketSummary.vencidos):'—','Requieren atención inmediata'],
  [Building2,'Empresas activas','3','Fase inicial'],[UsersRound,'Contactos','3','Autorizados'],[FolderKanban,'Proyectos activos','8','2 en riesgo'],[Server,'Activos monitoreados','146','12 críticos'],[CheckCircle2,'Cumplimiento SLA',ticketSummary?`${cumplimiento}%`:'—','Sobre tickets activos'],[Clock3,'Sin asignar',ticketSummary?String(ticketSummary.sin_asignar):'—','Pendientes de asignación'],
 ] as const;
 return <div className="space-y-7">
  <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-blue-950 via-slate-950 to-cyan-950 p-7 text-white shadow-2xl sm:p-10">
   <p className="text-xs font-black uppercase tracking-[.28em] text-cyan-300">IT Service Pro</p>
   <div className="mt-3 flex flex-wrap items-end justify-between gap-4"><div><h1 className="text-3xl font-black sm:text-4xl">{c.title}</h1><p className="mt-2 max-w-2xl text-white/70">{c.subtitle}</p></div><span className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold">{user?.rol}</span></div>
  </section>
  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{metrics.map(([Icon,label,value,note])=><article className="card" key={label}><div className="mb-4 grid h-11 w-11 place-items-center rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300"><Icon size={21}/></div><p className="text-sm text-slate-500">{label}</p><p className="mt-1 text-2xl font-black">{value}</p><p className="mt-2 text-xs text-slate-400">{note}</p></article>)}</div>
  <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]"><section className="card"><h2 className="text-lg font-black">Fundación habilitada</h2><p className="mt-1 text-sm text-slate-500">Módulos base disponibles para las siguientes fases.</p><div className="mt-5 grid gap-3 sm:grid-cols-2">{(data?.modulos||[]).map((x:string)=><div key={x} className="rounded-2xl border border-slate-200 p-4 font-bold dark:border-slate-800">{x}</div>)}</div></section><section className="card"><h2 className="text-lg font-black">Próximos pasos</h2><div className="mt-5 space-y-4">{['CRM empresarial y contactos','Motor profesional de tickets','SLA y mesa de ayuda','Proyectos, CMDB y facturación'].map((x,i)=><div className="flex gap-3" key={x}><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-blue-600 text-xs font-black text-white">{i+1}</span><p className="font-semibold">{x}</p></div>)}</div></section></div>
 </div>;
}
