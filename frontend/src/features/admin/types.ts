/** KPI date range as inclusive local dates (YYYY-MM-DD) in Philippine time;
 * null means unbounded on that side. UI state, sent as query params. */
export type KpiDateRange = { startDate: string | null; endDate: string | null }
