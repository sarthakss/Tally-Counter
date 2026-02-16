import React, { useState, useMemo } from 'react'
import { Search, Package, Clock, RefreshCw } from 'lucide-react'
import { InventoryItem } from '../config/supabase'

interface InventoryListProps {
  items: InventoryItem[]
  loading: boolean
  error: string | null
  lastSync: Date | null
  onRefresh: () => void
}

export const InventoryList: React.FC<InventoryListProps> = ({
  items,
  loading,
  error,
  lastSync,
  onRefresh
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')

  const categories = useMemo(() => {
    const cats = ['All', ...new Set(items.map(item => item.category))]
    return cats.sort()
  }, [items])

  const filteredItems = useMemo(() => {
    return items.filter(item => {
      const matchesSearch = 
        item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.item_code.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory
      
      return matchesSearch && matchesCategory
    })
  }, [items, searchTerm, selectedCategory])

  const formatLastSync = (date: Date | null) => {
    if (!date) return 'Never'
    
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const getStockStatusColor = (stock: number) => {
    if (stock <= 0) return 'text-red-600 bg-red-50'
    if (stock <= 5) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-2" />
          <p className="text-gray-600">Loading inventory...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-center space-x-2 text-red-700">
          <Package className="h-5 w-5" />
          <span className="font-medium">Error loading inventory</span>
        </div>
        <p className="text-red-600 mt-1">{error}</p>
        <button 
          onClick={onRefresh}
          className="btn-primary mt-3"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with sync status */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-gray-500" />
            <span className="text-sm text-gray-600">
              Last sync: {formatLastSync(lastSync)}
            </span>
          </div>
          <button
            onClick={onRefresh}
            className="p-2 text-gray-500 hover:text-primary-600 transition-colors"
            title="Refresh inventory"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Search and filters */}
      <div className="card space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search items by name or code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-1">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Items list */}
      <div className="space-y-2">
        {filteredItems.length === 0 ? (
          <div className="card text-center py-8">
            <Package className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">
              {searchTerm || selectedCategory !== 'All' 
                ? 'No items match your search criteria'
                : 'No inventory items found'
              }
            </p>
          </div>
        ) : (
          filteredItems.map(item => (
            <div key={item.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-medium text-gray-900 truncate">
                      {item.item_name}
                    </h3>
                    <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                      {item.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">
                    Code: {item.item_code}
                  </p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Physical: {item.physical_baseline}</span>
                    <span>Delta: {item.tally_delta >= 0 ? '+' : ''}{item.tally_delta}</span>
                    <span>Unit: {item.unit}</span>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStockStatusColor(item.current_stock)}`}>
                    {item.current_stock} {item.unit}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Summary */}
      {filteredItems.length > 0 && (
        <div className="card bg-gray-50">
          <div className="text-center text-sm text-gray-600">
            Showing {filteredItems.length} of {items.length} items
          </div>
        </div>
      )}
    </div>
  )
}
