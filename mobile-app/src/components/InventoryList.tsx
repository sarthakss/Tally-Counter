import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react'
import { Search, Package, Clock, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'
import { InventoryItem } from '../config/supabase'

// Optimized inventory item card component
const InventoryItemCard: React.FC<{
  item: InventoryItem
  getStockStatusColor: (stock: number) => string
}> = React.memo(({ item, getStockStatusColor }) => {
  return (
    <div className="card hover:shadow-md transition-shadow">
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
  )
})

interface InventoryListProps {
  items: InventoryItem[]
  loading: boolean
  error: string | null
  lastSync: Date | null
  onRefresh: () => void
}

export const InventoryList: React.FC<InventoryListProps> = React.memo(({
  items,
  loading,
  error,
  lastSync,
  onRefresh
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(50) // Pagination for performance
  const searchTimeoutRef = useRef<NodeJS.Timeout>()
  
  // Debounce search for better performance
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
      setCurrentPage(1) // Reset to first page on search
    }, 300)
    
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchTerm])

  const categories = useMemo(() => {
    const cats = ['All', ...new Set(items.map(item => item.category))]
    return cats.sort()
  }, [items])

  const filteredItems = useMemo(() => {
    if (!items.length) return []
    
    return items.filter(item => {
      const matchesSearch = !debouncedSearchTerm || 
        item.item_name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
        item.item_code.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
      
      const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory
      
      return matchesSearch && matchesCategory
    })
  }, [items, debouncedSearchTerm, selectedCategory])
  
  // Pagination calculations
  const totalPages = Math.ceil(filteredItems.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedItems = useMemo(() => {
    return filteredItems.slice(startIndex, endIndex)
  }, [filteredItems, startIndex, endIndex])
  
  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [selectedCategory])
  
  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page)
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])
  
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
  }, [])
  
  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category)
  }, [])

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
            onChange={handleSearchChange}
            className="input-field pl-10"
          />
          {debouncedSearchTerm !== searchTerm && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <RefreshCw className="h-4 w-4 animate-spin text-gray-400" />
            </div>
          )}
        </div>
        
        <div className="flex space-x-2 overflow-x-auto pb-1">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => handleCategoryChange(category)}
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
              {debouncedSearchTerm || selectedCategory !== 'All' 
                ? 'No items match your search criteria'
                : 'No inventory items found'
              }
            </p>
          </div>
        ) : (
          paginatedItems.map(item => (
            <InventoryItemCard key={item.id} item={item} getStockStatusColor={getStockStatusColor} />
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="card">
          <div className="flex items-center justify-between">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>
            
            <div className="flex items-center space-x-2">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i
                if (pageNum > totalPages) return null
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`px-3 py-1 text-sm font-medium rounded ${
                      currentPage === pageNum
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
      
      {/* Summary */}
      {filteredItems.length > 0 && (
        <div className="card bg-gray-50">
          <div className="text-center text-sm text-gray-600">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredItems.length)} of {filteredItems.length} items
            {filteredItems.length !== items.length && (
              <span className="text-gray-400"> (filtered from {items.length} total)</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
})
