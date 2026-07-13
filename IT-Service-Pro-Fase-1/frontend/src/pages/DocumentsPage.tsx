import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {File as FileIcon, FolderOpen, Loader2, Plus, Trash2, Upload} from 'lucide-react';
import {http, errorMessage, fileUrl} from '../api/http';
import {Modal} from '../components/Modal';
import type {Company, Document} from '../types';

export function DocumentsPage() {
  const qc = useQueryClient();
  const [empresaFiltro, setEmpresaFiltro] = useState('');
  const [open, setOpen] = useState(false);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [form, setForm] = useState({empresa_id: '', nombre: '', categoria: 'Contrato', visible_portal: true});
  const [subiendo, setSubiendo] = useState(false);

  const {data: empresas = []} = useQuery({queryKey: ['itsp-companies-all'], queryFn: async () => (await http.get('/itsp/companies')).data as Company[]});
  const {data: documentos = [], isLoading} = useQuery({
    queryKey: ['documents', empresaFiltro],
    queryFn: async () => (await http.get('/documents', {params: {empresa_id: empresaFiltro || undefined}})).data as Document[],
  });

  const invalidate = () => qc.invalidateQueries({queryKey: ['documents']});
  const crear = useMutation({
    mutationFn: async () => {
      if (!archivo) throw new Error('Selecciona un archivo');
      const fd = new FormData();
      fd.append('archivo', archivo);
      const subida = await http.post('/uploads', fd, {headers: {'Content-Type': undefined}});
      const {url, tipo_mime, tamano_bytes} = subida.data.data;
      return http.post('/documents', {...form, nombre: form.nombre || archivo.name, url_archivo: url, tipo_mime, tamano_bytes});
    },
    onMutate: () => setSubiendo(true),
    onSuccess: () => {toast.success('Documento subido'); setOpen(false); setArchivo(null); setForm({empresa_id: '', nombre: '', categoria: 'Contrato', visible_portal: true}); invalidate()},
    onError: e => toast.error(errorMessage(e)),
    onSettled: () => setSubiendo(false),
  });
  const eliminar = useMutation({
    mutationFn: (id: string) => http.delete(`/documents/${id}`),
    onSuccess: () => {toast.success('Documento eliminado'); invalidate()},
    onError: e => toast.error(errorMessage(e)),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><FolderOpen className="text-blue-600" />Documentos</h1>
          <p className="text-slate-500">Contratos, manuales y archivos compartidos por empresa.</p>
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}><Plus size={17} />Subir documento</button>
      </div>

      <div className="card">
        <select className="field w-auto" value={empresaFiltro} onChange={e => setEmpresaFiltro(e.target.value)}>
          <option value="">Todas las empresas</option>
          {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
        </select>
      </div>

      {isLoading ? <div className="card">Cargando documentos...</div> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {documentos.map(d => (
            <article key={d.id} className="card">
              <div className="flex items-start justify-between gap-2">
                <a href={fileUrl(d.url_archivo)} target="_blank" rel="noreferrer" className="flex items-center gap-3 hover:text-blue-600">
                  <div className="grid h-11 w-11 place-items-center rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/50"><FileIcon size={18} /></div>
                  <div>
                    <p className="font-bold">{d.nombre}</p>
                    <p className="text-xs text-slate-400">{d.categoria}</p>
                  </div>
                </a>
                <button className="text-rose-500 hover:text-rose-700" onClick={() => {if (confirm('¿Eliminar este documento?')) eliminar.mutate(d.id)}}><Trash2 size={16} /></button>
              </div>
              <p className="mt-3 text-xs text-slate-500">{d.empresa_nombre}</p>
              <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                {d.visible_portal ? <span className="badge bg-emerald-100 text-emerald-700">Visible en portal</span> : <span className="badge bg-slate-200 text-slate-600">Solo interno</span>}
                <span>{d.subido_por_nombre}</span>
              </div>
            </article>
          ))}
          {documentos.length === 0 && <div className="card text-center text-slate-400 md:col-span-2 xl:col-span-3">No hay documentos todavía</div>}
        </div>
      )}

      <Modal open={open} title="Subir documento" onClose={() => setOpen(false)}>
        <form className="space-y-4" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
          <label><span className="label">Empresa</span>
            <select className="field" required value={form.empresa_id} onChange={e => setForm({...form, empresa_id: e.target.value})}>
              <option value="">Selecciona una empresa</option>
              {empresas.map(e => <option key={e.id} value={e.id}>{e.nombre_comercial || e.razon_social}</option>)}
            </select>
          </label>
          <label><span className="label">Nombre (opcional, usa el del archivo si lo dejas vacío)</span>
            <input className="field" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
          </label>
          <label><span className="label">Categoría</span>
            <input className="field" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})} />
          </label>
          <label className="block">
            <span className="label">Archivo</span>
            <label className="mt-1 flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 py-6 text-sm text-slate-500 hover:border-blue-400 hover:text-blue-500 dark:border-slate-700">
              {subiendo ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
              {archivo ? archivo.name : 'Selecciona un archivo'}
              <input type="file" className="hidden" onChange={e => setArchivo(e.target.files?.[0] || null)} />
            </label>
          </label>
          <label className="flex items-center gap-2 text-sm font-semibold"><input type="checkbox" checked={form.visible_portal} onChange={e => setForm({...form, visible_portal: e.target.checked})} />Visible para el cliente en su portal</label>
          <div className="flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending || !archivo}>{crear.isPending ? 'Subiendo...' : 'Subir'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
