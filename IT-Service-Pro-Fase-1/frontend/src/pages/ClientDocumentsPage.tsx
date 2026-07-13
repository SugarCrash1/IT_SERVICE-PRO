import {useQuery} from '@tanstack/react-query';
import {File as FileIcon, FolderOpen} from 'lucide-react';
import {http, fileUrl} from '../api/http';
import type {Document} from '../types';

export function ClientDocumentsPage() {
  const {data: documentos = [], isLoading} = useQuery({
    queryKey: ['client-documents'],
    queryFn: async () => (await http.get('/client-portal/documents')).data.data as Document[],
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title flex items-center gap-2"><FolderOpen className="text-blue-600" />Documentos</h1>
        <p className="text-slate-500">Contratos, manuales y archivos que compartimos con tu empresa.</p>
      </div>

      {isLoading ? (
        <div className="card">Cargando documentos...</div>
      ) : documentos.length === 0 ? (
        <div className="card text-center text-slate-500">Aún no hay documentos compartidos con tu empresa.</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {documentos.map(d => (
            <a key={d.id} href={fileUrl(d.url_archivo)} target="_blank" rel="noreferrer" className="card flex items-center gap-3 hover:-translate-y-0.5 hover:shadow-lg transition">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/50"><FileIcon size={20} /></div>
              <div>
                <p className="font-bold">{d.nombre}</p>
                <p className="text-xs text-slate-400">{d.categoria} · {new Date(d.created_at).toLocaleDateString('es-PE')}</p>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
