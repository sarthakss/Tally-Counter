import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'YOUR_SUPABASE_URL'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type InventoryItem = {
  id: string
  item_code: string
  item_name: string
  category: string
  unit: string
  current_stock: number
  physical_baseline: number
  tally_delta: number
  last_sync: string
  sync_source: string
}
