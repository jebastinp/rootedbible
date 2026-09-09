import { useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2, ArrowRight, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { cn } from '@/lib/utils'
import AdminPageHeader from '../components/AdminPageHeader'

type FileType = 'users' | 'reading_plan' | 'progress'

interface PreviewRow {
  row_number: number
  data: Record<string, any>
  valid: boolean
  errors: string[]
  action: string
}
interface PreviewResponse {
  file_type: string
  total_rows: number
  valid_rows: number
  invalid_rows: number
  rows: PreviewRow[]
  import_token: string
}
interface ImportResult {
  file_type: string
  status: string
  total_rows: number
  inserted_rows: number
  updated_rows: number
  skipped_rows: number
  failed_rows: number
  errors: string[]
}

const FILE_TYPE_INFO: Record<FileType, { label: string; columns: string[] }> = {
  users: { label: 'users.csv', columns: ['user_id', 'name', 'role', 'phone', 'joined_date'] },
  reading_plan: { label: 'reading_plan.csv', columns: ['day', 'date', 'old_testament', 'new_testament', 'estimated_minutes'] },
  progress: { label: 'progress.csv', columns: ['user_id', 'day', 'completed', 'completed_date'] },
}

export default function AdminCsvImportPage() {
  const [fileType, setFileType] = useState<FileType>('users')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [uploading, setUploading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const { data: history } = useQuery({
    queryKey: ['import-history'],
    queryFn: async () => (await api.get('/admin/csv-import/history')).data,
  })

  async function handleUpload() {
    if (!file) return
    setUploading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file_type', fileType)
      formData.append('file', file)
      const { data } = await api.post<PreviewResponse>('/admin/csv-import/preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setPreview(data)
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setUploading(false)
    }
  }

  async function handleConfirm() {
    if (!preview) return
    setConfirming(true)
    try {
      const formData = new FormData()
      formData.append('import_token', preview.import_token)
      const { data } = await api.post<ImportResult>('/admin/csv-import/confirm', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
      toast.success('Import completed successfully')
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setConfirming(false)
    }
  }

  function reset() {
    setFile(null)
    setPreview(null)
    setResult(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div>
      <AdminPageHeader title="CSV Import" description="Bulk import members, reading plan, and progress data" />

      <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-5">
          {/* Step 1: choose file type + upload */}
          <div className="bg-surface rounded-3xl p-6 shadow-soft">
            <h3 className="font-semibold mb-4">1. Choose file & type</h3>
            <div className="flex gap-2 mb-4">
              {(Object.keys(FILE_TYPE_INFO) as FileType[]).map((ft) => (
                <button
                  key={ft}
                  onClick={() => {
                    setFileType(ft)
                    reset()
                  }}
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    fileType === ft ? 'bg-primary text-white' : 'bg-ink/5 text-ink-soft'
                  )}
                >
                  {FILE_TYPE_INFO[ft].label}
                </button>
              ))}
            </div>
            <p className="text-xs text-ink-soft mb-4">
              Required columns: <span className="font-mono">{FILE_TYPE_INFO[fileType].columns.join(', ')}</span>
            </p>

            <label className="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-ink/15 rounded-2xl py-10 cursor-pointer hover:border-secondary hover:bg-secondary/5 transition-colors">
              <UploadCloud size={28} className="text-ink-soft" />
              <span className="text-sm font-medium text-ink-soft">{file ? file.name : 'Click to select a CSV file'}</span>
              <input
                ref={inputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => {
                  setFile(e.target.files?.[0] ?? null)
                  setPreview(null)
                  setResult(null)
                }}
              />
            </label>

            {file && !preview && (
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="mt-4 w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark disabled:opacity-60"
              >
                {uploading ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
                Validate & Preview
              </button>
            )}
          </div>

          {/* Step 2: preview */}
          {preview && !result && (
            <div className="bg-surface rounded-3xl p-6 shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">2. Preview & confirm</h3>
                <button onClick={reset} className="text-xs text-ink-soft flex items-center gap-1 hover:text-ink">
                  <RotateCcw size={13} /> Start over
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-background rounded-xl p-3 text-center">
                  <div className="text-xl font-bold">{preview.total_rows}</div>
                  <div className="text-[11px] text-ink-soft">Total Rows</div>
                </div>
                <div className="bg-secondary/10 rounded-xl p-3 text-center">
                  <div className="text-xl font-bold text-primary">{preview.valid_rows}</div>
                  <div className="text-[11px] text-ink-soft">Valid</div>
                </div>
                <div className="bg-red-50 rounded-xl p-3 text-center">
                  <div className="text-xl font-bold text-red-600">{preview.invalid_rows}</div>
                  <div className="text-[11px] text-ink-soft">Invalid</div>
                </div>
              </div>

              <div className="max-h-64 overflow-y-auto rounded-xl border border-ink/5 mb-4">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-background">
                    <tr>
                      <th className="px-3 py-2 text-left">#</th>
                      <th className="px-3 py-2 text-left">Data</th>
                      <th className="px-3 py-2 text-left">Action</th>
                      <th className="px-3 py-2 text-left">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.rows.map((row) => (
                      <tr key={row.row_number} className="border-t border-ink/5">
                        <td className="px-3 py-2">{row.row_number}</td>
                        <td className="px-3 py-2 font-mono truncate max-w-[240px]">{JSON.stringify(row.data)}</td>
                        <td className="px-3 py-2 capitalize">{row.action}</td>
                        <td className="px-3 py-2">
                          {row.valid ? (
                            <span className="flex items-center gap-1 text-secondary"><CheckCircle2 size={13} /> Valid</span>
                          ) : (
                            <span className="flex items-center gap-1 text-red-600" title={row.errors.join(', ')}>
                              <XCircle size={13} /> {row.errors[0]}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <button
                onClick={handleConfirm}
                disabled={confirming || preview.valid_rows === 0}
                className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark disabled:opacity-60"
              >
                {confirming ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
                Confirm Import ({preview.valid_rows} rows)
              </button>
            </div>
          )}

          {/* Step 3: result */}
          {result && (
            <div className="bg-surface rounded-3xl p-6 shadow-soft">
              <h3 className="font-semibold mb-4">3. Import complete</h3>
              <div className="grid grid-cols-4 gap-3 mb-4">
                <Stat label="Inserted" value={result.inserted_rows} color="text-secondary" />
                <Stat label="Updated" value={result.updated_rows} color="text-primary" />
                <Stat label="Skipped" value={result.skipped_rows} color="text-gold" />
                <Stat label="Failed" value={result.failed_rows} color="text-red-600" />
              </div>
              {result.errors.length > 0 && (
                <div className="bg-red-50 rounded-xl p-3 text-xs text-red-700 max-h-32 overflow-y-auto mb-4">
                  {result.errors.map((e, i) => (
                    <div key={i}>{e}</div>
                  ))}
                </div>
              )}
              <button onClick={reset} className="w-full bg-primary/10 text-primary font-semibold py-3 rounded-xl hover:bg-primary/15">
                Import Another File
              </button>
            </div>
          )}
        </div>

        {/* Import history sidebar */}
        <div className="bg-surface rounded-3xl p-6 shadow-soft h-fit">
          <h3 className="font-semibold mb-4">Import History</h3>
          <div className="space-y-3">
            {history?.items?.map((h: any) => (
              <div key={h.id} className="border-b border-ink/5 pb-3 last:border-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{h.file_name}</span>
                  <span
                    className={cn(
                      'text-[10px] px-2 py-0.5 rounded-full capitalize',
                      h.status === 'success' && 'bg-secondary/15 text-primary',
                      h.status === 'failed' && 'bg-red-100 text-red-700',
                      h.status === 'rolled_back' && 'bg-red-100 text-red-700'
                    )}
                  >
                    {h.status}
                  </span>
                </div>
                <p className="text-[11px] text-ink-soft mt-1">
                  {h.inserted_rows} inserted · {h.updated_rows} updated · {h.failed_rows} failed
                </p>
              </div>
            ))}
            {!history?.items?.length && <p className="text-sm text-ink-soft">No imports yet.</p>}
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-background rounded-xl p-3 text-center">
      <div className={cn('text-xl font-bold', color)}>{value}</div>
      <div className="text-[11px] text-ink-soft">{label}</div>
    </div>
  )
}
