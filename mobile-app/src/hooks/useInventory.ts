import { useState, useEffect } from 'react'
import { supabase, InventoryItem } from '../config/supabase'

export const useInventory = () => {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastSync, setLastSync] = useState<Date | null>(null)

  const fetchItems = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch inventory items from the view
      const { data, error: fetchError } = await supabase
        .from('inventory_view')
        .select('*')
        .order('item_name')

      if (fetchError) {
        throw fetchError
      }

      setItems(data || [])

      // Get latest sync timestamp
      const { data: syncData, error: syncError } = await supabase
        .rpc('get_latest_sync_timestamp')

      if (!syncError && syncData) {
        setLastSync(new Date(syncData))
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch inventory')
      console.error('Error fetching inventory:', err)
    } finally {
      setLoading(false)
    }
  }

  const refreshItems = () => {
    fetchItems()
  }

  useEffect(() => {
    fetchItems()

    // Set up real-time subscription for updates
    const subscription = supabase
      .channel('inventory_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'stock_levels'
        },
        () => {
          fetchItems()
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  return {
    items,
    loading,
    error,
    lastSync,
    refreshItems
  }
}
