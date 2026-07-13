import {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {BookOpen, Eye, Plus, Search} from 'lucide-react';
import {http, errorMessage} from '../api/http';
import {Modal} from '../components/Modal';
import type {KnowledgeArticle} from '../types';

const emptyForm = {titulo: '', contenido: '', categoria: 'General', publicado: true};

export function KnowledgePage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [reading, setReading] = useState<KnowledgeArticle | null>(null);
  const [form, setForm] = useState(emptyForm);

  const {data: articulos = [], isLoading} = useQuery({
    queryKey: ['knowledge', search],
    queryFn: async () => (await http.get('/knowledge', {params: {busqueda: search || undefined}})).data as KnowledgeArticle[],
  });

  const crear = useMutation({
    mutationFn: () => http.post('/knowledge', form),
    onSuccess: () => {toast.success('Artículo publicado'); setOpen(false); setForm(emptyForm); qc.invalidateQueries({queryKey: ['knowledge']})},
    onError: e => toast.error(errorMessage(e)),
  });
  const abrir = useMutation({
    mutationFn: (id: string) => http.get(`/knowledge/${id}`),
    onSuccess: r => setReading(r.data as KnowledgeArticle),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2"><BookOpen className="text-blue-600" />Base de conocimiento</h1>
          <p className="text-slate-500">Soluciones y procedimientos reutilizables para el equipo técnico.</p>
        </div>
        <button className="btn-primary" onClick={() => setOpen(true)}><Plus size={17} />Nuevo artículo</button>
      </div>

      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-slate-400" size={18} />
          <input className="field pl-10" placeholder="Buscar en título o contenido" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      {isLoading ? <div className="card">Cargando artículos...</div> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {articulos.map(a => (
            <button key={a.id} onClick={() => abrir.mutate(a.id)} className="card text-left hover:-translate-y-0.5 hover:shadow-lg transition">
              <span className="badge bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{a.categoria}</span>
              <h2 className="mt-2 font-black">{a.titulo}</h2>
              <p className="mt-1 line-clamp-2 text-sm text-slate-500">{a.contenido}</p>
              <p className="mt-3 flex items-center gap-1 text-xs text-slate-400"><Eye size={12} />{a.vistas} vistas · {a.autor_nombre || 'Sistema'}</p>
            </button>
          ))}
          {articulos.length === 0 && <div className="card text-center text-slate-400 md:col-span-2 xl:col-span-3">No hay artículos todavía</div>}
        </div>
      )}

      <Modal open={open} title="Nuevo artículo" onClose={() => setOpen(false)}>
        <form className="space-y-4" onSubmit={e => {e.preventDefault(); crear.mutate()}}>
          <label><span className="label">Título</span><input className="field" required value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} /></label>
          <label><span className="label">Categoría</span><input className="field" value={form.categoria} onChange={e => setForm({...form, categoria: e.target.value})} /></label>
          <label><span className="label">Contenido</span><textarea className="field" required rows={8} value={form.contenido} onChange={e => setForm({...form, contenido: e.target.value})} /></label>
          <div className="flex justify-end gap-2">
            <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
            <button className="btn-primary" disabled={crear.isPending}>Publicar</button>
          </div>
        </form>
      </Modal>

      <Modal open={!!reading} title={reading?.titulo || ''} onClose={() => setReading(null)}>
        {reading && <div className="space-y-3 whitespace-pre-wrap text-sm">{reading.contenido}</div>}
      </Modal>
    </div>
  );
}
