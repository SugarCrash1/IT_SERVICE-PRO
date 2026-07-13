import {NavLink,Outlet} from 'react-router-dom';
import {useAuth} from '../auth/AuthContext';
import {LayoutDashboard,Building2,UsersRound,TicketCheck,Headphones,FolderKanban,BriefcaseBusiness,Server,Boxes,ShoppingCart,FileText,BarChart3,ShieldCheck,LogOut,Moon,Sun,Menu,X,Wrench,BookOpen,Clock3,FolderOpen,Truck} from 'lucide-react';
import {useState} from 'react';

const items: Array<[string,string,any,string[]]>=[
 ['/','Dashboard',LayoutDashboard,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/empresas','Empresas',Building2,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/contactos','Contactos',UsersRound,['ADMINISTRADOR','COORDINADOR']],
 ['/servicios-ti','Servicios TI',Wrench,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/tickets','Tickets',TicketCheck,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/mesa-ayuda','Mesa de ayuda',Headphones,['ADMINISTRADOR','COORDINADOR']],
 ['/proyectos','Proyectos',FolderKanban,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/contratos','Contratos',BriefcaseBusiness,['ADMINISTRADOR','COORDINADOR']],
 ['/timesheet','Horas',Clock3,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/cmdb','CMDB',Server,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/inventario-ti','Inventario',Boxes,['ADMINISTRADOR','COORDINADOR']],
 ['/guias-remision','Guías de remisión',Truck,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/compras-ti','Compras',ShoppingCart,['ADMINISTRADOR']],
 ['/facturacion','Facturación',FileText,['ADMINISTRADOR']],
 ['/documentos','Documentos',FolderOpen,['ADMINISTRADOR','COORDINADOR']],
 ['/conocimiento','Conocimiento',BookOpen,['ADMINISTRADOR','COORDINADOR','TECNICO']],
 ['/reportes-ti','Reportes',BarChart3,['ADMINISTRADOR','COORDINADOR']],
 ['/auditoria-ti','Auditoría',ShieldCheck,['ADMINISTRADOR']],
] as const;

export function AppLayout(){
 const{user,logout}=useAuth();
 const[dark,setDark]=useState(document.documentElement.classList.contains('dark'));
 const[open,setOpen]=useState(false);
 const toggle=()=>{document.documentElement.classList.toggle('dark');setDark(v=>!v)};

 return <div className="min-h-screen">
  <aside className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-slate-950 p-4 text-white shadow-2xl transition lg:translate-x-0 ${open?'translate-x-0':'-translate-x-full'}`}>
   <div className="mb-7 flex shrink-0 items-center justify-between px-2">
    <div className="flex items-center gap-3">
     <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 font-black">IT</div>
     <div><p className="text-xs font-black uppercase tracking-[.24em] text-cyan-300">IT Service</p><h1 className="text-lg font-black">Pro</h1></div>
    </div>
    <button className="lg:hidden" onClick={()=>setOpen(false)}><X/></button>
   </div>

   <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto">
    {items.filter(([, , ,roles])=>roles.includes(user?.rol||'')).map(([to,label,Icon])=>
     <NavLink key={to} to={to} end={to==='/'} onClick={()=>setOpen(false)}
      className={({isActive})=>`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold ${isActive?'bg-blue-600 text-white shadow-lg shadow-blue-950/30':'text-slate-300 hover:bg-white/10 hover:text-white'}`}>
      <Icon size={18}/>{label}
     </NavLink>
    )}
   </nav>

   <button onClick={logout} className="mt-2 flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-slate-300 hover:bg-rose-500/20 hover:text-rose-200">
    <LogOut size={19}/>Cerrar sesión
   </button>
  </aside>

  <div className="lg:pl-72">
   <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-white/90 px-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 sm:px-7">
    <button className="lg:hidden" onClick={()=>setOpen(true)}><Menu/></button>
    <div><p className="text-sm font-black">{user?.nombre_completo}</p><p className="text-xs font-semibold text-blue-600">{user?.rol}</p></div>
    <button className="btn-secondary !p-2.5" onClick={toggle}>{dark?<Sun size={18}/>:<Moon size={18}/>}</button>
   </header>
   <main className="p-4 sm:p-7"><Outlet/></main>
  </div>
 </div>
}