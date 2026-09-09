import { useEffect, useState } from 'react'
import { Wand2, Loader2, AlertTriangle, CheckCircle2, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { api, getApiErrorMessage } from '@/lib/api'
import { useBibleVersions } from '@/lib/bible'
import { cn } from '@/lib/utils'
import AdminPageHeader from '../components/AdminPageHeader'

type Section = 'new_testament' | 'full_bible' | 'gospels' | 'psalms' | 'custom'
type RestDay = 'none' | 'sunday' | 'one_per_week'
type GroupType = 'adult' | 'youth' | 'children' | 'family'

interface PlanDayPreview {
  day_number: number
  reading_date: string
  old_testament: string | null
  new_testament: string | null
  is_rest_day: boolean
}
interface PreviewResponse {
  total_days: number
  reading_days: number
  rest_days: number
  total_chapters: number
  approx_chapters_per_day: number
  days: PlanDayPreview[]
}

const SECTIONS: { value: Section; label: string }[] = [
  { value: 'new_testament', label: 'New Testament' },
  { value: 'full_bible', label: 'Full Bible' },
  { value: 'gospels', label: 'Gospels' },
  { value: 'psalms', label: 'Psalms' },
  { value: 'custom', label: 'Custom Books' },
]
const DURATIONS = [30, 90, 180, 365]

export default function AdminPlanGeneratorPage() {
  const [section, setSection] = useState<Section>('new_testament')
  const [customBooks, setCustomBooks] = useState('')
  const [startDate, setStartDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [duration, setDuration] = useState(90)
  const [restDay, setRestDay] = useState<RestDay>('sunday')
  const [groupType, setGroupType] = useState<GroupType>('adult')
  const [bibleVersionCode, setBibleVersionCode] = useState('')

  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [committing, setCommitting] = useState(false)
  const [confirmCommit, setConfirmCommit] = useState(false)
  const [committed, setCommitted] = useState<number | null>(null)
  const versions = useBibleVersions()

  useEffect(() => {
    if (!bibleVersionCode && versions.data?.length) {
      setBibleVersionCode(versions.data[0].code)
    }
  }, [bibleVersionCode, versions.data])

  function buildPayload() {
    return {
      section,
      custom_books: section === 'custom' ? customBooks.split(',').map((b) => b.trim()).filter(Boolean) : null,
      bible_version_code: bibleVersionCode,
      start_date: startDate,
      duration_days: duration,
      rest_day: restDay,
      group_type: groupType,
    }
  }

  async function handlePreview() {
    if (!bibleVersionCode) {
      toast.error('No approved Bible edition is available yet')
      return
    }
    setLoadingPreview(true)
    setCommitted(null)
    try {
      const { data } = await api.post<PreviewResponse>('/admin/plan-generator/preview', buildPayload())
      setPreview(data)
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setLoadingPreview(false)
    }
  }

  async function handleCommit() {
    if (!bibleVersionCode) {
      toast.error('No approved Bible edition is available yet')
      return
    }
    setCommitting(true)
    try {
      const { data } = await api.post<{ days_written: number }>('/admin/plan-generator/commit', buildPayload())
      setCommitted(data.days_written)
      setConfirmCommit(false)
      toast.success(`Plan saved - ${data.days_written} reading days created`)
    } catch (err) {
      toast.error(getApiErrorMessage(err))
    } finally {
      setCommitting(false)
    }
  }

  return (
    <div>
      <AdminPageHeader
        title="Reading Plan Generator"
        description="Auto-distribute chapters across a challenge duration, per the plan's chapter formula"
      />

      <div className="p-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Config form */}
        <div className="lg:col-span-1 space-y-5">
          {versions.isSuccess && !versions.data.length && (
            <div role="status" className="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
              No approved Bible editions are available. Complete the edition licensing and content review before generating a plan.
            </div>
          )}

          <div className="bg-surface rounded-3xl p-6 shadow-soft space-y-4">
            <h3 className="font-semibold mb-1">Challenge Settings</h3>

            <div>
              <label htmlFor="plan-bible-version" className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Bible Edition</label>
              <select
                id="plan-bible-version"
                value={bibleVersionCode}
                disabled={!versions.data?.length}
                className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm disabled:opacity-50"
                onChange={(event) => setBibleVersionCode(event.target.value)}
              >
                {!versions.data?.length && <option value="">No approved editions available</option>}
                {versions.data?.map((version) => <option key={version.code} value={version.code}>{version.version_name} · {version.language}</option>)}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Bible Section</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {SECTIONS.map((s) => (
                  <button
                    key={s.value}
                    onClick={() => setSection(s.value)}
                    className={cn(
                      'px-3 py-2 rounded-xl text-sm font-medium transition-colors',
                      section === s.value ? 'bg-primary text-white' : 'bg-ink/5 text-ink-soft'
                    )}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
              {section === 'custom' && (
                <input
                  value={customBooks}
                  onChange={(e) => setCustomBooks(e.target.value)}
                  placeholder="e.g. Genesis, Exodus, Matthew"
                  className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm"
                />
              )}
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Duration</label>
              <div className="grid grid-cols-4 gap-2 mt-2">
                {DURATIONS.map((d) => (
                  <button
                    key={d}
                    onClick={() => setDuration(d)}
                    className={cn(
                      'py-2 rounded-xl text-sm font-medium',
                      duration === d ? 'bg-primary text-white' : 'bg-ink/5 text-ink-soft'
                    )}
                  >
                    {d}d
                  </button>
                ))}
              </div>
              <input
                type="number"
                min={1}
                max={730}
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value || '0', 10))}
                className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Rest Days</label>
              <select value={restDay} onChange={(e) => setRestDay(e.target.value as RestDay)} className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm">
                <option value="none">None - read every day</option>
                <option value="sunday">Sunday rest</option>
                <option value="one_per_week">One rest day per week</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-ink-soft uppercase tracking-wide">Group Type</label>
              <select value={groupType} onChange={(e) => setGroupType(e.target.value as GroupType)} className="mt-2 w-full rounded-xl border border-ink/10 px-3 py-2 text-sm">
                <option value="adult">Adult</option>
                <option value="youth">Youth</option>
                <option value="children">Children</option>
                <option value="family">Family</option>
              </select>
            </div>

            <button
              onClick={handlePreview}
              disabled={loadingPreview}
              className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark disabled:opacity-60"
            >
              {loadingPreview ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
              Generate Preview
            </button>
          </div>
        </div>

        {/* Preview */}
        <div className="lg:col-span-2 space-y-5">
          {!preview && (
            <div className="bg-surface rounded-3xl p-10 shadow-soft text-center text-ink-soft">
              Configure a challenge on the left, then generate a preview before saving.
            </div>
          )}

          {preview && (
            <div className="bg-surface rounded-3xl p-6 shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Preview</h3>
                <button onClick={() => { setPreview(null); setCommitted(null) }} className="text-xs text-ink-soft flex items-center gap-1 hover:text-ink">
                  <RotateCcw size={13} /> Start over
                </button>
              </div>

              <div className="grid grid-cols-4 gap-3 mb-4">
                <Stat label="Total Days" value={preview.total_days} />
                <Stat label="Reading Days" value={preview.reading_days} />
                <Stat label="Rest Days" value={preview.rest_days} />
                <Stat label="Chapters/Day" value={preview.approx_chapters_per_day} />
              </div>

              <div className="max-h-80 overflow-y-auto rounded-xl border border-ink/5 mb-4">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-background">
                    <tr>
                      <th className="px-3 py-2 text-left">Day</th>
                      <th className="px-3 py-2 text-left">Date</th>
                      <th className="px-3 py-2 text-left">Reading</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.days.map((d) => (
                      <tr key={d.day_number} className="border-t border-ink/5">
                        <td className="px-3 py-2">{d.day_number}</td>
                        <td className="px-3 py-2">{d.reading_date}</td>
                        <td className="px-3 py-2">
                          {d.is_rest_day ? (
                            <span className="text-ink-soft italic">Rest day</span>
                          ) : (
                            <span>{[d.old_testament, d.new_testament].filter(Boolean).join(' + ')}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {committed !== null ? (
                <div className="flex items-center gap-2 bg-secondary/10 text-primary rounded-xl p-3 text-sm font-medium">
                  <CheckCircle2 size={16} /> Saved - {committed} reading days written to the live plan.
                </div>
              ) : !confirmCommit ? (
                <button
                  onClick={() => setConfirmCommit(true)}
                  className="w-full flex items-center justify-center gap-2 bg-primary text-white font-semibold py-3 rounded-xl shadow-soft hover:bg-primary-dark"
                >
                  Save This Plan
                </button>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 space-y-3">
                  <p className="text-sm text-red-700 flex items-start gap-2">
                    <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                    This replaces your <strong>entire</strong> current reading plan - any manually
                    edited days will be lost. Continue?
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCommit}
                      disabled={committing}
                      className="flex-1 bg-red-600 text-white font-semibold py-2.5 rounded-xl disabled:opacity-60"
                    >
                      {committing ? 'Saving...' : 'Yes, replace the plan'}
                    </button>
                    <button onClick={() => setConfirmCommit(false)} className="flex-1 bg-white border border-ink/10 font-semibold py-2.5 rounded-xl">
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-background rounded-xl p-3 text-center">
      <div className="text-xl font-bold text-primary">{value}</div>
      <div className="text-[11px] text-ink-soft">{label}</div>
    </div>
  )
}
